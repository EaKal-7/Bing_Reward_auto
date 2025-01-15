import time
import random
import os
import logging
import re
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium_stealth import stealth
import requests
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

# 配置日志记录
logging.basicConfig(
    filename='bing_rewards_bot.log',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    encoding='utf-8'
)

# 常量定义
TARGET_PC_POINTS = 90   # PC端积分目标 (已自动获取，本项报废)
TARGET_MOBILE_POINTS = 60   # 移动端积分目标(已自动获取，本项报废)
ENABLE_PC_POINT_LIMIT = True   # 是否启用PC端积分限制
ENABLE_MOBILE_POINT_LIMIT = True   # 是否启用移动端积分限制
RANGE_SEARCH = 250   # 搜索次数
SKIP_PC_SEARCH = False   # 是否跳过PC端搜索

# 关键词来源列表
SEARCH_KEY_SOURCES = [
    {"name": "bilibili", "url": "https://api-hot.imsyy.top/bilibili"},
    {"name": "acfun", "url": "https://api-hot.imsyy.top/acfun"},
    {"name": "weibo", "url": "https://api-hot.imsyy.top/weibo"},
    {"name": "zhihu", "url": "https://api-hot.imsyy.top/zhihu"},
    {"name": "zhihu-daily", "url": "https://api-hot.imsyy.top/zhihu-daily"},
    {"name": "baidu", "url": "https://api-hot.imsyy.top/baidu"},
    {"name": "douyin", "url": "https://api-hot.imsyy.top/douyin"},
    {"name": "douban-movie", "url": "https://api-hot.imsyy.top/douban-movie"},
    {"name": "douban-group", "url": "https://api-hot.imsyy.top/douban-group"},
    {"name": "tieba", "url": "https://api-hot.imsyy.top/tieba"},
    {"name": "sspai", "url": "https://api-hot.imsyy.top/sspai"},
    {"name": "ithome", "url": "https://api-hot.imsyy.top/ithome"},
    {"name": "ithome-xijiayi", "url": "https://api-hot.imsyy.top/ithome-xijiayi"},
    {"name": "jianshu", "url": "https://api-hot.imsyy.top/jianshu"},
    {"name": "guokr", "url": "https://api-hot.imsyy.top/guokr"},
    {"name": "thepaper", "url": "https://api-hot.imsyy.top/thepaper"},
    {"name": "toutiao", "url": "https://api-hot.imsyy.top/toutiao"},
    {"name": "36kr", "url": "https://api-hot.imsyy.top/36kr"},
    {"name": "51cto", "url": "https://api-hot.imsyy.top/51cto"},
    {"name": "csdn", "url": "https://api-hot.imsyy.top/csdn"},
    {"name": "nodeseek", "url": "https://api-hot.imsyy.top/nodeseek"},
    {"name": "juejin", "url": "https://api-hot.imsyy.top/juejin"},
    {"name": "qq-news", "url": "https://api-hot.imsyy.top/qq-news"},
    {"name": "sina", "url": "https://api-hot.imsyy.top/sina"},
    {"name": "sina-news", "url": "https://api-hot.imsyy.top/sina-news"},
    {"name": "netease-news", "url": "https://api-hot.imsyy.top/netease-news"},
    {"name": "52pojie", "url": "https://api-hot.imsyy.top/52pojie"},
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

def fetch_keywords_from_api(min_count=777):
    """
    从多个API获取关键词，确保至少获取min_count条。
    如果不足则用默认关键词补足。
    """
    all_keywords = set()
    
    for source in SEARCH_KEY_SOURCES:
        url = source["url"]
        name = source["name"]
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get("code") == 200 and "data" in data:
                for item in data["data"]:
                    keyword = item.get("title")
                    if keyword:
                        all_keywords.add(keyword.strip())
            
            logging.info(f"从 '{name}' 获取了 {len(data.get('data', []))} 个关键词。")
            
            if len(all_keywords) >= min_count:
                break  # 达到所需数量，停止请求
        except requests.exceptions.RequestException as e:
            logging.error(f"从 '{name}' 获取关键词失败：{e}")
            continue  # 继续尝试下一个来源
    
    # 如果总数不足，则用默认关键词补足
    if len(all_keywords) < min_count:
        needed = min_count - len(all_keywords)
        additional = random.sample(default_keywords, min(needed, len(default_keywords)))
        all_keywords.update(additional)
        logging.info(f"使用默认关键词补足了 {len(additional)} 个关键词。")
    
    # 如果仍不足min_count条（默认关键词不足），则返回现有数量
    return list(all_keywords)[:min_count]

def get_mobile_points(driver):
    """
    通过界面交互获取移动端当前的积分值。

    参数:
    - driver: Selenium WebDriver 实例

    返回:
    - 积分值（int）或 None
    """
    try:
        driver.refresh()  # 刷新页面以确保积分数值是最新的
        # 定位并点击SVG元素以展开积分菜单
        svg_element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "svg.b_serphb"))
        )
        svg_element.click()
        logging.info("已点击移动端积分菜单按钮。")

        # 等待积分元素可见
        points_span = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "fly_id_rc"))
        )

        # 提取积分文本并转换为整数
        points_text = points_span.text.strip()
        points = int(points_text)
        logging.info(f"[移动端] 当前积分：{points}")

        return points

    except Exception as e:
        logging.error(f"获取移动端积分时发生错误: {e}")
        return None


def get_current_points(driver, is_mobile=False):        #获取的是总分数
    """
    获取当前的积分值。
    根据驱动器的上下文（PC 或移动端），选择不同的元素来解析积分数值。
    
    参数:
    - driver: Selenium WebDriver 实例
    - is_mobile: 布尔值，是否为移动端驱动器
    
    返回:
    - 积分值（int）或 None
    """
    try:
        if is_mobile:
            points = get_mobile_points(driver)
            return points
        else:
            # 定位 PC 端积分的 div 元素
            points_div = driver.find_element("id", "rh_rwm")
            aria_label = points_div.get_attribute("aria-label")
            # 解析积分数值
            match = re.search(r'Microsoft Rewards (\d+)', aria_label)
            if match:
                points = int(match.group(1))
                # logging.info(f"[PC端] 当前积分：{points}")
                return points
            else:
                logging.warning("未能在aria-label中找到积分信息。")
                return None
    except Exception as e:
        if is_mobile:
            logging.error(f"[移动端] 获取积分失败：{e}")
        else:
            logging.error(f"[PC端] 获取积分失败：{e}")
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
    options.add_argument("profile-directory=Profile 2")

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

def get_initial_points(driver, is_mobile=False):
    try:
        driver.get("https://rewards.bing.com/pointsbreakdown")  # 访问积分详情页面
        logging.info("已打开积分详情页面。")
        time.sleep(random.uniform(3, 5))  # 等待页面加载
        points_span = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((
                By.XPATH,
                "//span[@mee-element-ready='$ctrl.loadCounterAnimation()' and @tabindex='0' and contains(@aria-label, ',')]"
            ))
        )
        points_text = points_span.text.strip()  # e.g., "12,249"
        points = int(points_text.replace(",", ""))  # 移除逗号并转换为整数
        # 获取 PC 端积分 (从 <p> 标签中提取)
        pc_points_text = driver.find_element("xpath", "//p[contains(@class, 'pointsDetail') and contains(text(), ' / 90')]").text
        # 提取 PC 端当前分数
        pc_current_points = int(re.search(r"(\d+)", pc_points_text).group(1))
        pc_required_points = 90 - pc_current_points  # 计算剩余的 PC 端积分
        logging.info(f"PC 端当前积分：{pc_current_points}，剩余所需积分：{pc_required_points}")

        # 获取移动端积分 (从 <p> 标签中提取)
        mobile_points_text = driver.find_element("xpath", "//p[contains(@class, 'pointsDetail') and contains(text(), ' / 60')]").text
        # 提取移动端当前分数
        mobile_current_points = int(re.search(r"(\d+)", mobile_points_text).group(1))
        mobile_required_points = 60 - mobile_current_points  # 计算剩余的移动端积分
        logging.info(f"移动端当前积分：{mobile_current_points}，剩余所需积分：{mobile_required_points}")

        if is_mobile:
            return mobile_current_points,mobile_required_points,points
        else:
            return pc_current_points,pc_required_points,points
    except Exception as e:
        logging.error(f"获取积分信息失败：{e}")
        return None, None

def perform_searches(driver, search_terms, target_points=None, is_mobile=False, last_points=None):
    """
    执行搜索任务，监控积分变化。
    如果积分变化超过 target_points，则停止搜索。

    参数:
    - driver: Selenium WebDriver 实例
    - search_terms: 搜索关键词列表
    - target_points: 积分目标（可选）
    - is_mobile: 布尔值，是否为移动端驱动器
    - last_points: 上一次获取的积分值，用于计算本轮积分

    返回:
    - final_points: 执行搜索后的最终积分值
    """
    # initial_points = last_points
    # if initial_points is None:
    try:
        _,_,initial_points = get_initial_points(driver, is_mobile)
        if initial_points is not None:
            logging.info(f"初始积分：{initial_points}")
            last_points = initial_points
        else:
            logging.warning("无法获取初始积分。")
    except Exception as e:
        logging.error(f"访问 Bing 搜索页面失败：{e}")

    if initial_points is None and target_points is not None:
        logging.warning("无法获取初始积分，无法监控积分变化。")

    try:
        driver.get("https://www.bing.com")
        logging.info("已打开 Bing 搜索页面。")
        time.sleep(random.uniform(2, 5))  # 在页面加载后随机等待几秒

        # 执行搜索
        for i in range(RANGE_SEARCH):
            search_term = random.choice(search_terms)  # 选择随机搜索词
            try:
                # 有时Bing会动态加载搜索框，可多次尝试获取
                for attempt in range(3):
                    try:
                        search_box = driver.find_element(By.NAME, "q")
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
                    driver.execute_script("window.scrollTo(0,0);")
                    logging.debug("返回顶部。")
                    time.sleep(random.uniform(1, 2))

                # 在下一次搜索前，随机等待较长时间，避免固定间隔
                wait_time = random.uniform(20, 40)
                logging.debug(f"等待 {wait_time:.2f} 秒后进行下一次搜索。")
                time.sleep(wait_time)

                # 检测积分变化
                if initial_points is not None and target_points is not None:
                    try:
                        current_points = get_current_points(driver, is_mobile)  #获取的是当前总分
                        if current_points is not None:
                            gained_points = current_points - initial_points
                            temp_points = current_points - last_points
                            logging.info(f"当前积分：{current_points}/{target_points+initial_points}，本轮获得积分：{gained_points},本次获得积分：{temp_points}")
                            if gained_points >= target_points:
                                logging.info(f"积分增加超过{target_points+initial_points}（{target_points}），停止搜索。")
                                break  # 跳出循环，停止搜索
                            else:
                                last_points = current_points  # 更新初始积分
                        else:
                            logging.warning("无法获取当前积分。")
                    except Exception as e:
                        logging.error(f"检测积分时发生错误：{e}")

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
        final_points = get_current_points(driver, is_mobile)
        if final_points is not None:
            logging.info(f"最终积分：{final_points}")
        else:
            logging.warning("无法获取最终积分。")
    except Exception as e:
        logging.error(f"访问 Bing Rewards 页面失败：{e}")

    return initial_points

def get_required_points(driver):
    """
    从 Bing Rewards 积分详情页获取 PC 端和移动端的所需积分。
    返回一个元组 (pc_required_points, mobile_required_points)
    """
    try:
        driver.get("https://rewards.bing.com/pointsbreakdown")  # 访问积分详情页面
        logging.info("已打开积分详情页面。")
        time.sleep(random.uniform(3, 5))  # 等待页面加载

        # 获取 PC 端积分 (从 <p> 标签中提取)
        pc_points_text = driver.find_element("xpath", "//p[contains(@class, 'pointsDetail') and contains(text(), ' / 90')]").text
        # 提取 PC 端当前分数
        pc_current_points = int(re.search(r"(\d+)", pc_points_text).group(1))
        pc_required_points = 90 - pc_current_points  # 计算剩余的 PC 端积分
        logging.info(f"PC 端当前积分：{pc_current_points}，剩余所需积分：{pc_required_points}")

        # 获取移动端积分 (从 <p> 标签中提取)
        mobile_points_text = driver.find_element("xpath", "//p[contains(@class, 'pointsDetail') and contains(text(), ' / 60')]").text
        # 提取移动端当前分数
        mobile_current_points = int(re.search(r"(\d+)", mobile_points_text).group(1))
        mobile_required_points = 60 - mobile_current_points  # 计算剩余的移动端积分
        logging.info(f"移动端当前积分：{mobile_current_points}，剩余所需积分：{mobile_required_points}")

        return pc_required_points, mobile_required_points
    except Exception as e:
        logging.error(f"获取积分信息失败：{e}")
        return None, None

def main():
    # 通过上述函数获取500条关键词
    search_terms = fetch_keywords_from_api()
    logging.info(f"总共获取到 {len(search_terms)} 条关键词。")
    
    # 设置 Chrome 用户配置路径
    profile_path = r"C:\\Users\\XXXX\\AppData\\Local\\Google\\Chrome\\User Data"  # 根据自己的配置修改

    # 执行 PC 端搜索
    logging.info("开始 PC 端搜索任务。")
    pc_driver = setup_driver(profile_path)
    if pc_driver:
        # 获取 PC 和移动端所需的积分
        pc_required_points, mobile_required_points = get_required_points(pc_driver)

        # 执行 PC 端搜索
        if not SKIP_PC_SEARCH and pc_required_points > 0:
            perform_searches(pc_driver, search_terms, target_points=pc_required_points if ENABLE_PC_POINT_LIMIT else None, is_mobile=False,last_points=0)
        try:
            pc_driver.quit()
            logging.info("PC 浏览器已成功关闭。")
        except Exception as e:
            logging.error(f"关闭 PC 浏览器时发生错误：{e}")
    else:
        logging.error("未能初始化 PC 端 WebDriver，跳过 PC 端搜索任务。")
    
    # 等待一段时间后执行移动端搜索
    logging.info("等待 10 秒后开始移动端搜索任务。")
    time.sleep(10)
    
    # 移动端仿真参数
    mobile_emulation = {
        "deviceName": "iPhone 12 Pro"
    }

    # 执行移动端搜索
    logging.info("开始移动端搜索任务。")
    mobile_driver = setup_driver(profile_path, mobile_emulation=mobile_emulation)
    if mobile_driver:
        # 获取移动端初始积分
        _,_,initial_mobile_points = get_initial_points(mobile_driver, is_mobile=True)
        if initial_mobile_points is None:
            logging.error("无法获取移动端初始积分，跳过移动端搜索任务。")
            initial_mobile_points = 0  # 使用默认值
        
        # 执行移动端搜索
        final_mobile_points = perform_searches(
            mobile_driver, 
            search_terms, 
            target_points=mobile_required_points if ENABLE_MOBILE_POINT_LIMIT else None, 
            is_mobile=True, 
            last_points=initial_mobile_points
        )
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
