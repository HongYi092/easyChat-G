import os
import subprocess
import sys
import time
import readline

MAX_RETRIES = 3


def install_package(package):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    except subprocess.CalledProcessError:
        print(f"安装包失败: {package}")
        return False
    return True


def scan_and_install_packages(script_path):
    with open(script_path, 'r') as file:
        lines = file.readlines()

    packages = set()
    for line in lines:
        if line.startswith('import '):
            package = line.split('import ')[1].strip()
            if '.' in package:
                package = package.split('.')[0]
            packages.add(package)
        elif line.startswith('from '):
            package = line.split('from ')[1].split(' import ')[0].strip()
            packages.add(package)

    for package in packages:
        try:
            __import__(package)
        except ModuleNotFoundError:
            print(f"模块 '{package}' 未找到。正在尝试安装...")
            if not install_package(package):
                return False
    return True


def find_startup_script(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                script_path = os.path.join(root, file)
                return script_path
    return None


def clone_repo():
    repo = input("输入存储库（格式：author/repo）: ")
    url = f"https://github.com/{repo}.git"
    repo_name = repo.split('/')[-1]
    try:
        subprocess.check_call(['git', 'clone', url])
        os.chdir(repo_name)
        print(f"已将目录克隆并更改为 {repo_name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"克隆存储库失败: {e}")
        return False


def main_menu():
    options = ["Download GitHub repository", "Start script", "Exit"]
    while True:
        print("\n请选择一个选项:")
        for idx, option in enumerate(options, 1):
            print(f"{idx}. {option}")

        choice = input("输入您选择的号码: ")
        if choice == "1":
            if clone_repo():
                scan_menu()
        elif choice == "2":
            script_path = find_startup_script(os.getcwd())
            if script_path:
                execute_script(script_path)
            else:
                print("未找到启动脚本.")
        elif choice == "3":
            sys.exit(0)
        else:
            print("选择无效。请重试.")


def scan_menu():
    options = ["Start script scanning", "Return to main menu"]
    while True:
        print("\n请选择一个选项:")
        for idx, option in enumerate(options, 1):
            print(f"{idx}. {option}")

        choice = input("输入您选择的号码: ")
        if choice == "1":
            script_path = find_startup_script(os.getcwd())
            if script_path:
                if scan_and_install_packages(script_path):
                    execute_script(script_path)
                else:
                    print("扫描和安装软件包失败.")
            else:
                print("未找到启动脚本.")
            break
        elif choice == "2":
            os.chdir("..")
            break
        else:
            print("选择无效。请重试.")


def execute_script(script_path):
    retries = 0
    while retries < MAX_RETRIES:
        try:
            subprocess.check_call([sys.executable, script_path])
            print("脚本执行成功.")
            return
        except subprocess.CalledProcessError as e:
            error_message = str(e)
            print(f"执行脚本时出错: {error_message}")
            missing_package = parse_missing_package(error_message)
            if missing_package:
                if install_package(missing_package):
                    retries += 1
                    print(f"正在重试... ({retries}/{MAX_RETRIES})")
                else:
                    break
            else:
                break
        time.sleep(1)  # Adding a small delay before retrying
    print("已达到最大重试次数。退出.")


def parse_missing_package(error_message):
    if "ModuleNotFoundError: No module named" in error_message:
        missing_module = error_message.split("No module named ")[1].strip("'")
        return missing_module
    return None


if __name__ == "__main__":
    main_menu()
