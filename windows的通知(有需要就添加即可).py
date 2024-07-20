from plyer import notification

def show_notification(title, message):
    notification.notify(
        title=title,
        message=message,
        app_icon=None,  # 应用程序图标的路径。
        timeout=10,  # 持续时间（秒）
    )

# 示例调用
show_notification("新消息", "你有来自Steven的新消息！")
