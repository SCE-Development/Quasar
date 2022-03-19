const util = require("./util.js");
const { inkLevel } = util;

inkLevel("right").then((result) => {
  console.log(result);
});
