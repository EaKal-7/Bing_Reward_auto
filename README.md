- # Bing Rewards Bot

  This project automates daily search tasks on Bing to help you earn Microsoft Rewards points. By simulating realistic user behaviors—such as typing keywords character by character, random scrolling, varied waiting times, and switching between PC and mobile browsing modes—it aims to reduce the likelihood of detection as an automated script.

  ## Features

  - **PC and Mobile Searches**: Perform searches in both a normal desktop environment and a simulated mobile environment to meet diverse Microsoft Rewards search requirements.
  - **Randomized Keyword Selection**: Fetch trending keywords from multiple sources (e.g., Baidu, Weibo, Douyin) to ensure variety. If these APIs don’t provide enough keywords, a default local keyword list will supplement them.
  - **Points Monitoring and Limits**: Set points thresholds to stop searching once you’ve gained a certain number of points, preventing unnecessary or suspiciously high volumes of searches.
  - **Detailed Logging**: Utilize Python’s `logging` module to write execution logs to `bing_rewards_bot.log`, allowing you to review and analyze search activities and performance.

  ## Requirements

  - Python 3.7+ (Python 3.8 or higher recommended)
  - Required Python packages:
    - `selenium`
    - `selenium-stealth`
    - `requests`
    - `logging` (part of Python’s standard library)

  You will also need a matching ChromeDriver version for your installed Chrome browser.

  If you haven’t installed `selenium-stealth`:

  ```bash
  pip install selenium-stealth
  ```

  ## Setup and Usage

  1. **Add `chromedriver.exe` to System PATH**:
     Make sure `chromedriver.exe` is in your system PATH. You can place it in a directory already in PATH or add a new directory to PATH. 

  2. **Install Dependencies**:

     ```bash
     pip install selenium requests selenium-stealth
     ```

  3. **Configure Chrome User Data Directory**:
     Update the `profile_path` in the script to point to your local Chrome user data directory. For example:

     ```python
     profile_path = r"C:\\Users\\YourUserName\\AppData\\Local\\Google\\Chrome\\User Data"
     ```

     Make sure that the `profile-directory` parameter aligns with your actual Chrome profile folder.

  4. **Run the Script**:

     ```bash
     python bing_rewards_bot.py
     ```

     The script will first run searches in PC mode, then wait 60 seconds, and finally run searches in mobile emulation mode. Logs will be recorded in `bing_rewards_bot.log`.

  ## Configuration

  - `TARGET_PC_POINTS` and `TARGET_MOBILE_POINTS`:
    Sets the number of points to earn before stopping on PC and mobile modes, respectively, if enabled.
  - `ENABLE_PC_POINT_LIMIT` and `ENABLE_MOBILE_POINT_LIMIT`:
    Toggle whether to enforce the points limit on PC and mobile modes.
  - `SEARCH_KEY_SOURCES`:
    Add, remove, or modify the list of data sources for trending keywords.
  - `default_keywords`:
    Default keywords to supplement fetched keywords if the sources do not provide enough. Feel free to expand this list as needed.

  ## Logging and Debugging

  All runtime logs are written to `bing_rewards_bot.log`, including:

  - Executed search terms
  - Current points readings
  - Errors and warnings during execution

  Refer to the log file for insights into script performance and troubleshooting.

  ## Notes and Disclaimer

  - **For Educational and Research Purposes Only**:
    This script is intended to demonstrate automation techniques. Do not use it in ways that violate Microsoft’s or Bing’s terms of service.
  - **Risk of Detection**: Although the script includes random delays, scrolling, and varying search keywords to reduce detection, there is still a risk that automated activities could be flagged, leading to account warnings or bans. Use at your own risk.
  - **Maintenance**: Keep your browser and ChromeDriver updated to ensure compatibility and stable operation.