# Comics publisher
This program allows you to download random comics from 
[xkcd](https://xkcd.com/) and publish it on your group wall
in [vk](https://vk.com).

### How to Install

Python3 should be already installed. Then use pip (or pip3,
if there is a conflict with Python2) to install dependencies:
```
pip install -r requirements.txt
```
To run most **vk** API methods you need to pass 
**access_token** - a special access key. The most easiest
way to obtain it is to use Implicit Flow method
1. Create a group in vk.
2. Create new application in [My Apps](https://vk.com/apps?act=manage).
3. Application type should be *standalone*.
4. In your app settings please copy **App ID**, create
*.env** file and save there your App ID as 
```CLIENT_ID = your App ID```.
5. Form the following link:
<https://oauth.vk.com/authorize?client_id=xxx&display=page&scope=photos,groups,wall,offline&response_type=token&v=yyy>
where xxx should be replaced with your CLIENT_ID from 
**.env** file and yyy with the actual API version.
More detailed information can be found in [documentation for
Implicit Flow](https://vk.com/dev/implicit_flow_user).
6. You will receive response in browser address bar
with the following key **access_token=very long string**.
Copy this string and save to your **.env** file as 
```ACCESS_TOKEN = your access token```.
7. Get your group ID from address of your group. Save it
in **.env** file as ```GROUP_ID = your group ID```.

### Project Goals
The code is written for educational purposes on online-course 
for web-developers [dvmn.org](https://dvmn.org).