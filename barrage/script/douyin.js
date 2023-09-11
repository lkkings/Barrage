var Barrage = class {
    propsId = null
    chatRoomDom = null
    joinRoomDom = null
    joinRoomObserver = null
    chatRoomObserver = null
    options = null
    ws = null
    constructor(options={wsurl:"ws://127.0.0.1:9999",timeinterval:1000}) {
        this.options = options
        this.propsId = Object.keys(document.querySelector('.webcast-chatroom___list'))[1]
        this.chatRoomDom = document.querySelector('.webcast-chatroom___items').children[0]
        this.joinRoomDom = document.querySelector('.webcast-chatroom___bottom-message')
    }

    run(){
        //打开定时器重连
        let timer;
        this.ws = new WebSocket(this.options.wsurl)
        this.ws.onclose = () => {
            timer = setInterval(() => {
                console.log('正在等待服务器启动..')
                this.ws = new WebSocket(this.options.wsurl);
                console.log('状态 ->', this.ws.readyState)
            }, this.options.timeinterval)
        }
        this.ws.onopen = () => {
             console.log(`[${new Date().toLocaleTimeString()}]`, '服务已经连接成功!')
            //关闭定时器
            clearInterval(timer)
            this.enableListener()
        }
    }
    enableListener() {

        this.joinRoomObserver = new MutationObserver((mutationsList) => {
            for (let mutation of mutationsList) {
                if (mutation.type === 'childList' && mutation.addedNodes.length) {
                    let dom = mutation.addedNodes[0]
                    let user = dom[this.propsId].children.props.message.payload.user
                    if(user){
                        let data = Object.assign({action:"join"},this.getUser(user))
                        this.ws.send(JSON.stringify(data))
                        console.log("join",data)
                    }

                }
            }
        });
        this.joinRoomObserver.observe(this.joinRoomDom, { childList: true });
        this.chatRoomObserver = new MutationObserver((mutationsList, observer) => {
            for (let mutation of mutationsList) {
                if (mutation.type === 'childList' && mutation.addedNodes.length) {
                    let dom = mutation.addedNodes[0]
                    let body = dom[this.propsId].children.props.message.payload;
                    if (body.user){
                        let data = Object.assign(this.getUser(body.user))
                        if (body.common.method === "WebcastGiftMessage")
                            data = Object.assign({action:"gift"},data,this.getGift(body))
                        else
                            data = Object.assign({action:"message"},data,this.getMessage(body))
                        this.ws.send(JSON.stringify(data))
                        console.log("message",data)
                    }

                }
            }
        });
        this.chatRoomObserver.observe(this.chatRoomDom, { childList: true });
    }

    getUser(user){
        return {
            user_avatar : user.avatar_thumb.url_list[0],
            user_level: user.badge_image_list[0]? user.badge_image_list[0].content.level:0,
            user_id: user.id,
            nickname: user.nickname,
            gender: user.gender === 1 ? '男' : '女',
            is_admin: user.user_attr.is_admin,
        }
    }

    getGift(body){
        return {
            gift_id: body.gift_id,
            gift_name: body.gift.name,
            gift_number: parseInt(body.repeatCount),
            describe:body.common.describe
        }
    }

    getMessage(body){
        return {content:body.content}
    }


}

var barrage = new Barrage({wsurl:arguments[0],timeinterval:arguments[1]})
barrage.run()

