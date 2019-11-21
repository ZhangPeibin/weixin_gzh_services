var fs = require("fs")
var exec = require("child_process").exec;
var url = require("url")

function execPythonToDealHtml(_biz,file,offset){
    var python_name = "history_details_process.py"
    exec('python'+' '+python_name + ' '+_biz+' '+file+' '+offset,function(err,stdout,stderr){
    if(err)
        {
            console.log('stderr',err);
        }

    if(stdout)
        {
            console.log('stdout',stdout);
        }
    });
}

function saveHttpContent(_biz,file,data,offset){
    var f_dir = "tmp/"+_biz+"/"
    fs.exists(f_dir, function(exists) {
        if(!exists){
            fs.mkdir(f_dir)
        }
    });
    var f = f_dir + file
    fs.writeFile(f,data,{flag:'w'},function(err){
        if (err){
            return console.error(err)
        }
        console.log("数据写入成功")
        console.log("开始解析公众号数据")
        execPythonToDealHtml(_biz,f,offset)
    });
}

var home = "https://mp.weixin.qq.com/mp/profile_ext?action=home"
var getmsg = "https://mp.weixin.qq.com/mp/profile_ext?action=getmsg"

function filter(url){
    if(url.indexOf(home) != -1 ||
        url.indexOf(getmsg) != -1){
        return true
    }
    return false
}

function process_wei_xin_url(requestDetail_url,response){
    var path = url.parse(requestDetail_url,true).query
    biz = path.__biz
    offset = 0
    if (requestDetail_url.indexOf(home) != -1){
        offset = 0
    }else if(requestDetail_url.indexOf(getmsg) != -1){
        offset = path.offset
    }
    const newResponse = response;
    var obj = JSON.stringify(newResponse)
    saveHttpContent(biz,offset+".html",newResponse.body,offset)
}

module.exports = {
  summary: 'a rule to hack response',
  *beforeSendResponse(requestDetail, responseDetail) {
    // 历史消息
    if (filter(requestDetail.url)) {
        process_wei_xin_url(requestDetail.url,responseDetail.response)
        return new Promise((resolve, reject) => {
            setTimeout(() => { // delay
            resolve({ response: responseDetail.response });
            }, 5000);
        });
    }
  },
};