const app = require('express')();
const multer = require('multer')
const fs = require('fs')
const python = require('python-shell');
const http = require('http').createServer(app);

const port = process.env.PORT || 8080;

http.listen(port, () => {
    console.log(`App Runs on ${port}`)
})

let io = require('socket.io')(http);

io.on("connection", (socket) => {
    console.log("a user connected");

    socket.on("disconnect", () => {
        console.log("a user disconnected");
    })
})

var storage = multer.diskStorage({
    destination: function (req, file, cb) {
        let dir = './core/images/' + req.body.id;
        if (!fs.existsSync(dir)){
            fs.mkdirSync(dir);
        }
        cb(null, './core/images/' + req.body.id + '/');
    },
    filename: function (req, file, cb) {
      cb(null, file.originalname)
    }
  })

const upload = multer({
    storage: storage, 
    limits: {fileSize: 10000000}
}).array('images', 24)


function checkProgress(id) {
    let raw = fs.readFileSync('progress.json');
    let progress = JSON.parse(raw)["progress"];
    io.emit("progress", {"id": id, "progress": progress})
}


app.post('/upload', (req, res) => {
    console.log("uploading files")
    upload(req, res, function (err) {
        if(req.body.key !== "dontplease") {
            res.status(400).json({message: "bad-key"})
        }
        else if (err) {
            res.status(400).json({message: err.message})
        } else {
            try {
                console.log("upload complete, starting bg removal")
                var options = {
                    args: [req.body.id],
                    mode: 'text'
                }
                var script = new python.PythonShell('./core/main.py', options);
                
                let pg = setInterval(() => checkProgress(req.body.id), 1000);

                script.on('message', (message) => {
                    if(message === "done") {
                        clearInterval(pg);
                        res.status(200).json({message: 'uploaded'})
                    } else if (message === "bad") {
                        clearInterval(pg);
                        res.status(400).json({message: "core"})
                    } else {
                        
                    }
                })
            } catch (err) {
                res.status(400).json({message: err})
            }
        }
    })
})

app.get("/", (req, res) => {
    res.status(200).json({message: "hi!"})
})

// router.get('/images/:imagename', (req, res) => {
//     let imagename = req.params.imagename
//     let imagepath = __dirname + "/images/" + imagename
//     let image = fs.readFileSync(imagepath)
//     let mime = fileType(image).mime

// 	res.writeHead(200, {'Content-Type': mime })
// 	res.end(image, 'binary')
// })

app.use((err, req, res, next) => {
    if (err.code == 'ENOENT') {
        res.status(404).json({message: 'Image Not Found !'})
    } else {
        res.status(500).json({message:err.message}) 
    } 
})


