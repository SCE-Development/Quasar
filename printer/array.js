const array = [ 'McDouble', 'Fries', 'apple pie'];
function printStuff(element){
    console.log(element);
}

array.map(printStuff);

const printStuffButArrow = (element) => {
    console.log(element);
}

array.map((element) => {
    console.log(element);
});

const mapResult = array.map((element) => {
    console.log(element);
    return 'lmao'
})
const forEachResult = array.forEach((element) => {
    console.log(element);
    return 'lmao'
})

console.log(forEachResult)


const forEachResult = 