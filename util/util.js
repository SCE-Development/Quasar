const { exec } = require('child_process');

function checkIp(ip) {
	return new Promise((resolve) => {
		const pingCommand = 'ping -c 4 ' + ip
		exec(pingCommand, function(error, stdout, stderr) {
			if(error) {
				resolve(false)
			}
			resolve(true)
	  });
	})	
}

module.exports = {checkIp}