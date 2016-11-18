import urllib2,urllib, json, threading, time

from_repeat = 392474616 #2000000000
to_repeat = 8 + 2000000000
token=''

pts_data = None
standert_delay = 5.0
delay = standert_delay

new_msg = []


def loClock():
    global delay
    global new_msg
    while True:
        time.sleep(delay)
        if getPostpone() == True:
            setPostpone(False)
            continue      
        SendMessages(new_msg[:])
        new_msg = []

isPostpone = False
def getPostpone():
    global isPostpone
    return isPostpone

def setPostpone(_set, _delay = False):
    global isPostpone
    global delay
    global standert_delay
    if _delay == False:
        delay = standert_delay
    else:
        delay = _delay       
    isPostpone = _set
    

def loPoll():
    global token
    global pts_data

    while True:     
        poll = API_link_requst('https://'+pts_data['server']+'?',token,
                              {'act':'a_check',
                               'key':pts_data['key'],
                               'ts':pts_data['ts'],
                               'wait':'25',
                               'mode':'32',
                               'version':'1' }
                              )
        if 'failed' in poll:
            pts_data = GetPTS(token)
            return False
        
        t_ProcessPoll = threading.Thread(target=ProcessPoll, args=(poll,))
        t_ProcessPoll.daemon = True
        t_ProcessPoll.start()
        
        pts_data['pts'] = poll['pts']
        pts_data['ts'] = poll['ts']
    
def ProcessPoll(poll):
    global from_repeat
    global new_msg
    updates=poll['updates']
    
    for i in range(0,len(updates)):
        if updates[i][0] == 4 and updates[i][3] == from_repeat:
            setPostpone(True)
            new_msg.append(updates[i][1])
    

def SendMessages(new_msg):
    global token
    global need_sent 
    if len(new_msg) == 0:
        return False
    
    response = API_request('messages.send',token,
                {'peer_id':to_repeat,
                 'forward_messages':','.join(map(str,new_msg)),
                 'v':'5.38'}
                )
    if not(type(response) is int):
        if 'error' in response:
            setPostpone(True,10)
            print 'Error from Sending Messages'
            time.sleep(5)
            print 'Repeat Sending Messages'
            SendMessages(new_msg)
            return False
    
    new_msg = []


def main():
    global token
    global pts_data
    global timer
    global delay

    pts_data = GetPTS(token)
    
    t_lPoll = threading.Thread(target=loPoll, args=())
    t_lPoll.daemon = True
    t_lPoll.start()


    t_lClock = threading.Thread(target=loClock, args=())
    t_lClock.daemon = True
    t_lClock.start()

    
    
def GetPTS(token):
    return API_request('messages.getLongPollServer',token,
                       {'use_ssl':'0',
                        'need_pts':'1'}
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
