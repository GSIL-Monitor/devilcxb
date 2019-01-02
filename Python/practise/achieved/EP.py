import urllib2   
from ntlm import HTTPNtlmAuthHandler   
   
user = 'xiaobo.chi'   
password = "DEVIL_cxb456"   
url = "http://ep.tclcom.com/"

user_sso = 'TA-CD\\xiaobo.chi'   
password_sso = "DEVIL_cxb456"   
url_sso = "http://epwf.tclcom.com/CDAttendanceRequest/CDAttendanceRequest.aspx" 
   
passman = urllib2.HTTPPasswordMgrWithDefaultRealm()   
passman.add_password(None, url, user, password)
passman.add_password(None, url_sso, user_sso, password_sso)
#print passman
# create the NTLM authentication handler   
auth_NTLM = HTTPNtlmAuthHandler.HTTPNtlmAuthHandler(passman)  
   
# other authentication handlers 
auth_basic = urllib2.HTTPBasicAuthHandler(passman) 
auth_digest = urllib2.HTTPDigestAuthHandler(passman) 
 
# disable proxies (if you want to stay within the corporate network) 
proxy_handler = urllib2.ProxyHandler({}) 
 
# create and install the opener 
opener = urllib2.build_opener(proxy_handler, auth_NTLM, auth_digest, auth_basic) 
urllib2.install_opener(opener) 
 
   
# retrieve the result
url2 = "http://ep.tclcom.com/Pages/default.aspx#"
response = urllib2.urlopen(url2)   
#print(response.read())


url3 = "http://ep.tclcom.com/Pages/SystemBusiness.aspx?categoryID=1"
response = urllib2.urlopen(url3)  
#print(response.read())

url4 = "http://epwf.tclcom.com/CDAttendanceRequest/CDAttendanceRequest.aspx"
req = urllib2.Request(url4)
handle = urllib2.urlopen(req)
print handle.read()
