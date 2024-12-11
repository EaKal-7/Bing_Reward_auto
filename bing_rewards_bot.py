import time
import random
import os
import logging
import re
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium_stealth import stealth
import requests

# 配置日志记录
logging.basicConfig(
    filename='bing_rewards_bot.log',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# 常量定义
TARGET_PC_POINTS = 90   # PC端积分目标
TARGET_MOBILE_POINTS = 60   # 移动端积分目标
ENABLE_PC_POINT_LIMIT = False   # 是否启用PC端积分限制
ENABLE_MOBILE_POINT_LIMIT = False   # 是否启用移动端积分限制

# 可用的数据源（与JS脚本中一致）
SEARCH_KEY_SOURCES = [
    ("百度热搜", "BaiduHot"),
    ("抖音热搜", "DouYinHot"),
    ("搜狗热搜", "SoGouHot"),
    ("360热搜", "SoHot"),
    ("微博热搜", "WeiBoHot"),
    ("知乎热搜", "ZhiHuHot"),
    ("今日头条", "TouTiaoHot"),
    ("快手热搜", "KuaiShouHot")
]

# 默认本地关键词，当无法获取或不足500时，补充用
default_keywords = [
    "python 编程", "AI 技术", "Web 开发", "云计算", 
    "数据科学", "机器学习", "人工智能", "JavaScript", 
    "数据库管理", "软件工程", "AWS 教程", "数据结构",
    "深度学习", "云安全", "前端开发", "后端开发", 
    "Python 库", "物联网", "网络安全", "区块链技术", "ReactJS", 
    "AngularJS", "Node.js", "Linux 命令", "SQL 查询", "Java 编程",
    "C++ 教程", "GitHub", "项目管理", "敏捷开发方法", 
    "DevOps 工具", "虚拟化", "Docker", "Kubernetes", "数据分析", 
    "大数据", "云计算服务", "Web 爬虫", "自动化", 
    "伦理黑客", "UI/UX 设计", "Git 命令", "云存储", 
    "DevOps 实践", "移动应用开发", "AI 伦理", "TensorFlow 教程", 
    "PyTorch 教程", "OpenAI 工具", "无服务器计算", "微服务架构", 
    "跨平台开发", "Java Spring Boot", "PHP 框架", "Ruby on Rails", 
    "自然语言处理", "计算机视觉", "自动驾驶", 
    "增强现实", "虚拟现实", "聊天机器人开发", "SEO 优化", 
    "内容管理系统", "数据可视化", "Power BI 教程", 
    "Tableau 教程", "网络安全", "量子计算", "边缘计算", 
    "游戏开发", "Unreal Engine", "Unity 游戏引擎", "移动端 UX 设计", 
    "渐进式 Web 应用", "智能合约", "数字营销", 
    "CRM 工具", "ERP 系统", "Python 金融", "Web 性能优化", 
    "响应式 Web 设计", "计算机图形学", "云原生开发", 
    "数据仓库", "分布式系统", "软件测试", "API 开发", 
    "RESTful 服务", "GraphQL", "网络协议", "渗透测试工具", 
    "加密技术", "R 编程", "Scala 编程", "Hadoop 生态系统", 
    "Apache Spark", "实时数据处理", "服务器管理", 
    "CI/CD 管道", "网络故障排除", "云成本优化", 
    "ChatGPT 集成", "机器人编程", "自动化框架", 
    "Python 爬虫", "技术文档", "技术职业", 
    "自由职业开发者", "区块链金融", "智能家居技术",
    # ... (您可以根据需要继续扩充)
]

def fetch_keywords_from_api(min_count=500):
    """
    从多个数据源获取关键词，确保至少获取min_count条。
    如果不足则用默认关键词补足。
    """
    all_keywords = set()
    # API基础URL
    base_url = "https://api.gumengya.com/Api/"
    # 尝试多个来源直到满足min_count
    random_sources = random.sample(SEARCH_KEY_SOURCES, len(SEARCH_KEY_SOURCES))
    for source_name, action in random_sources:
        # 请求API
        url = base_url + action
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            if data.get("code") == 200 and "data" in data:
                for item in data["data"]:
                    # 根据JS脚本逻辑，这里简单处理下标题
                    # 例如添加一些随机字符增加多样性
                    kw = f"{source_name} {item['title']} {''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=3))}"
                    all_keywords.add(kw)
            # 如果已经达到min_count条，就可以提前结束
            if len(all_keywords) >= min_count:
                break
        except Exception as e:
            # 如果某个来源获取失败，则继续尝试下一个来源
            logging.error(f"获取{source_name}词条失败：{e}")
            continue
    
    # 如果总数不足，则用默认关键词补足
    if len(all_keywords) < min_count:
        needed = min_count - len(all_keywords)
        # 随机从默认关键词中抽取所需数量(如果默认不够，就全部加上)
        additional = random.sample(default_keywords, min(needed, len(default_keywords)))
        all_keywords.update(additional)
    
    # 如果仍不足min_count条（默认关键词不足），则返回现有数量
    return list(all_keywords)

def get_current_points(driver):
    """
    获取当前的积分值。
    根据提供的HTML结构，解析aria-label属性中的积分数值。
    """
    try:
        # 定位包含积分的div
        points_div = driver.find_element("id", "rh_rwm")
        aria_label = points_div.get_attribute("aria-label")
        # 解析积分数值
        match = re.search(r'Microsoft Rewards (\d+)', aria_label)
        if match:
            points = int(match.group(1))
            logging.info(f"当前积分：{points}")
            return points
        else:
            logging.warning("未能在aria-label中找到积分信息。")
            return None
    except Exception as e:
        logging.error(f"获取积分失败：{e}")
        return None

def setup_driver(profile_path, mobile_emulation=None):
    """
    设置和初始化WebDriver。
    如果提供了mobile_emulation，则启用移动端仿真。
    """
    options = webdriver.ChromeOptions()

    # 清理DevToolsActivePort文件
    devtools_file = os.path.join(profile_path, 'DevToolsActivePort')
    if os.path.exists(devtools_file):
        try:
            os.remove(devtools_file)
            logging.info("已移除 DevToolsActivePort 文件以避免冲突。")
        except Exception as e:
            logging.error(f"移除 DevToolsActivePort 文件失败：{e}")

    if mobile_emulation:
        options.add_experimental_option("mobileEmulation", mobile_emulation)

    # 使用用户数据目录
    options.add_argument(f"user-data-dir={profile_path}")
    options.add_argument("profile-directory=Profile 1")

    # 一些隐匿和降低检测的配置项
    options.add_argument("--no-proxy-server")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--ignore-ssl-errors")
    options.add_argument("--disable-web-security")
    options.add_argument("--no-sandbox")
    options.add_argument("start-maximized")
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)

    # 初始化 WebDriver
    try:
        driver = webdriver.Chrome(options=options)
        logging.info("WebDriver 初始化成功。")
    except Exception as e:
        logging.error(f"WebDriver 初始化失败：{e}")
        return None

    # 使用 selenium-stealth 进一步隐藏
    stealth(driver,
            languages=["zh-CN", "zh", "en-US", "en"],
            plugins=["Chrome PDF Viewer", "Native Client"],
            vendor="Google Inc.",
            platform="iPhone" if mobile_emulation else "Win32",
            webgl_vendor="Apple Inc." if mobile_emulation else "Google Inc.",
            renderer="Apple GPU" if mobile_emulation else "ANGLE (Intel(R) HD Graphics 620 Direct3D11 vs_5_0 ps_5_0)",
            fix_hairline=True,
            screen_resolution=(375, 812) if mobile_emulation else (1920, 1080),
            proxy=None,
            use_adblock=True
    )

    return driver

def perform_searches(driver, search_terms, target_points=None):
    """
    执行搜索任务，监控积分变化。
    如果积分变化超过target_points，则停止搜索。
    """
    initial_points = None
    try:
        driver.get("https://www.bing.com/")
        logging.info("已打开 Bing Rewards 页面。")
        time.sleep(random.uniform(3, 5))  # 等待页面加载
        initial_points = get_current_points(driver)
        if initial_points is not None:
            logging.info(f"初始积分：{initial_points}")
        else:
            logging.warning("无法获取初始积分。")
    except Exception as e:
        logging.error(f"访问 Bing Rewards 页面失败：{e}")
    
    if initial_points is None and target_points is not None:
        logging.warning("无法获取初始积分，无法监控积分变化。")
    
    try:
        driver.get("https://www.bing.com")
        logging.info("已打开 Bing 搜索页面。")
        time.sleep(random.uniform(2, 5))  # 在页面加载后随机等待几秒
    
        # 执行100次搜索
        for i in range(100):
            search_term = random.choice(search_terms)  # 选择随机搜索词
            try:
                # 有时Bing会动态加载搜索框，可多次尝试获取
                for attempt in range(3):
                    try:
                        search_box = driver.find_element("name", "q")
                        break
                    except:
                        time.sleep(random.uniform(1, 3))
                else:
                    logging.warning(f"搜索框未找到，跳过搜索 {i+1}")
                    continue
                
                # 清空搜索框
                search_box.clear()
                time.sleep(random.uniform(0.5, 1.5))  # 模拟短暂思考时间

                # 模拟用户逐字输入关键词
                for char in search_term:
                    search_box.send_keys(char)
                    time.sleep(random.uniform(0.05, 0.2))  # 每个字符之间随机停顿

                # 按回车提交搜索
                search_box.send_keys(Keys.RETURN)
                logging.info(f"执行搜索 {i+1}: {search_term}")

                # 等待页面加载
                time.sleep(random.uniform(3, 6))

                # 模拟用户查看搜索结果的行为：
                # 随机滚动页面几次
                scroll_times = random.randint(1, 3)
                for _ in range(scroll_times):
                    # 随机滚动距离
                    scroll_distance = random.randint(100, 1000)
                    driver.execute_script(f"window.scrollBy(0, {scroll_distance});")
                    logging.debug(f"滚动页面：{scroll_distance} 像素")
                    time.sleep(random.uniform(1, 3))  # 浏览一下内容

                # 偶尔返回顶部，模拟用户上下滑动
                if random.random() < 0.3:
                    driver.execute_script("window.scrollTo(0,0);")
                    logging.debug("返回顶部。")
                    time.sleep(random.uniform(1, 2))

                # 在下一次搜索前，随机等待较长时间，避免固定间隔
                wait_time = random.uniform(20, 60)
                logging.debug(f"等待 {wait_time:.2f} 秒后进行下一次搜索。")
                time.sleep(wait_time)

                # 检测积分变化
                if initial_points is not None and target_points is not None:
                    try:
                        driver.get("https://www.bing.com/")
                        logging.info("已重新打开 Bing Rewards 页面以检测积分。")
                        time.sleep(random.uniform(2, 4))  # 等待页面加载
                        current_points = get_current_points(driver)
                        if current_points is not None:
                            logging.info(f"当前积分：{current_points}")
                            if current_points - initial_points >= target_points:
                                logging.info(f"积分增加超过{target_points}（{current_points - initial_points}），停止搜索。")
                                break  # 跳出循环，停止搜索
                        else:
                            logging.warning("无法获取当前积分。")
                    except Exception as e:
                        logging.error(f"检测积分时发生错误：{e}")

                # 返回 Bing 搜索页面继续搜索
                driver.get("https://www.bing.com")
                logging.info("返回 Bing 搜索页面。")
                time.sleep(random.uniform(2, 5))  # 等待页面加载

            except Exception as e:
                logging.error(f"执行搜索 {i+1} 时发生错误：{e}")
                # 遇到问题就刷新页面或重新打开 Bing
                time.sleep(random.uniform(2, 5))
                driver.get("https://www.bing.com")
                time.sleep(random.uniform(3, 6))

        logging.info("搜索任务完成。")
    
    except Exception as e:
        logging.error(f"执行搜索任务时发生错误：{e}")
    
    # 获取最终积分
    try:
        driver.get("https://www.bing.com/")
        logging.info("已打开 Bing Rewards 页面以获取最终积分。")
        time.sleep(random.uniform(2, 4))  # 等待页面加载
        final_points = get_current_points(driver)
        if final_points is not None:
            logging.info(f"最终积分：{final_points}")
        else:
            logging.warning("无法获取最终积分。")
    except Exception as e:
        logging.error(f"访问 Bing Rewards 页面失败：{e}")

def main():
    # 通过上述函数获取500条关键词
    search_terms = fetch_keywords_from_api(min_count=500)
    logging.info(f"总共获取到 {len(search_terms)} 条关键词。")
    
    # 设置 Chrome 用户配置路径
    profile_path = r"C:\\Users\\****\\AppData\\Local\\Google\\Chrome\\User Data"  # 根据自己的配置修改

    # 执行 PC 端搜索
    logging.info("开始 PC 端搜索任务。")
    pc_driver = setup_driver(profile_path)
    if pc_driver:
        perform_searches(pc_driver, search_terms, target_points=TARGET_PC_POINTS if ENABLE_PC_POINT_LIMIT else None)
        try:
            pc_driver.quit()
            logging.info("PC 浏览器已成功关闭。")
        except Exception as e:
            logging.error(f"关闭 PC 浏览器时发生错误：{e}")
    else:
        logging.error("未能初始化 PC 端 WebDriver，跳过 PC 端搜索任务。")
    
    # 等待一分钟后执行移动端搜索
    logging.info("等待 60 秒后开始移动端搜索任务。")
    time.sleep(60)
    
    # 移动端仿真参数
    mobile_emulation = {
        "deviceName": "iPhone X"
    }

    # 执行移动端搜索
    logging.info("开始移动端搜索任务。")
    mobile_driver = setup_driver(profile_path, mobile_emulation=mobile_emulation)
    if mobile_driver:
        perform_searches(mobile_driver, search_terms, target_points=TARGET_MOBILE_POINTS if ENABLE_MOBILE_POINT_LIMIT else None)
        try:
            mobile_driver.quit()
            logging.info("移动端浏览器已成功关闭。")
        except Exception as e:
            logging.error(f"关闭移动端浏览器时发生错误：{e}")
    else:
        logging.error("未能初始化移动端 WebDriver，跳过移动端搜索任务。")

    print("所有搜索任务完成。查看日志文件 'bing_rewards_bot.log' 以获取详细信息。")

if __name__ == "__main__":
    main()