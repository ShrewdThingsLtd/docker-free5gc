var http = require('http');
var static = require('node-static');
const { exec } = require("child_process");

var http_reply = function (req, res, txt) {

    res.write(txt); //write a response to the client
    res.end(); //end the response
}

var file_server = new static.Server("/opt/netgraph/public");

//create a server object:
http.createServer(function (req, res) {

    console.log(req.url);
    if(req.url === "/") {
        file_server.serveFile("./index.html", 200, {}, req, res);
    }
    else if(req.url === "/netgraph.svg") {
        exec("python /opt/netgraph/netgraph.py > /opt/netgraph/public/netgraph.svg", (error, stdout, stderr) => {

            if (error) {
                http_reply(req, res, `error: ${error.message}`);
                return;
            }
            if (stderr) {
                http_reply(req, res, `stderr: ${stderr}`);
                return;
            }
            console.log(`stdout: ${stdout}`);
            file_server.serveFile("./netgraph.svg", 200, {}, req, res);
        });
    }
    else {
        file_server.serve(req, res);
    }

}).listen(8080);
