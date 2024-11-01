const args = process.argv.slice(2)

const lowerBound = parseInt(args[0], 10);
const upperBound = parseInt(args[1], 10);
console.log(Math.floor(Math.random() * (upperBound - lowerBound) + lowerBound));
