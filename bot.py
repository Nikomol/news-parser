#Главный файл запуска
from channels import initialize_channels, monitor_channels

if __name__ == '__main__':
    initialize_channels()
    monitor_channels()
