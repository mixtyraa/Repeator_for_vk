import urllib2,urllib, json


from_repeat = 38775878 #+ 2000000000
to_repeat = 19 + 2000000000
token=''

def main():
    while True:
        pts = GetPTS(token)
        PollProccess(pts)
    
def GetPTS(token):
    return API_request('messages.getLongPollServer',token,
                       {'use_ssl':'0',
                        'need_pts':'1'}
                        )            

def PollProccess(pts_data):
    updates = API_link_requst('https://'+pts_data['server']+'?',token,
                              {'act':'a_check',
                               'key':pts_data['key'],
                               'ts':pts_data['ts'],
                               'wait':'25',
                               'version':'1' }
                              )
    updates=updates['updates']
    new_msg = []  
    for i in range(0,len(updates)):
        if updates[i][0] == 4 and updates[i][3] == from_repeat:
            new_msg.append(updates[i][1])
    if len(new_msg) > 0:  
        print API_request('messages.send',token,
                {'peer_id':to_repeat,
                 'forward_messages':(','.join(map(str,new_msg))),
                 'v':'5.38'}
                )
    
def API_request(method, token, params):
    url = 'https://api.vk.com/method/' + method
    return API_link_requst(url,token,params)

def API_link_requst(url,token,params):
    url += '?access_token='+token
    params = urllib.urlencode(params)
    hdr = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0',
           'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
           'Accept-Language':'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3'}   
    request = urllib2.Request(url, params,headers=hdr)
    response = urllib2.urlopen(request)
    html = response.read()
    try:
        return json.loads(html)['response']
    except:
        return json.loads(html)
    
if __name__ == '__main__':
    main()
