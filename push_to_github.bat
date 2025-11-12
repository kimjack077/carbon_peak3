@echo off
echo 正在准备将项目推送到GitHub...
echo.
echo 请确保您已经完成了以下步骤：
echo 1. 在GitHub上创建了名为"carbon_peak3"的仓库
echo 2. 将下面的命令中的"您的用户名"替换为您的GitHub用户名
echo.
set /p username=请输入您的GitHub用户名: 

echo.
echo 正在更新远程仓库地址...
git remote set-url origin https://github.com/%username%/carbon_peak3.git

echo.
echo 正在推送代码到GitHub...
git push -u origin master

echo.
echo 完成！您的项目已成功上传到GitHub
pause