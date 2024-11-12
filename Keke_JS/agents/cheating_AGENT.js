// BABA IS Y'ALL SOLVER - BLANK TEMPLATE
// Version 1.0
// Code by Milk


//get imports (NODEJS)
var simjs = require('../js/simulation')
const fs = require("fs");					//access the game states and simulation
var data1 = require('../json_levels/demo_LEVELS.json')
var data2 = require('../json_levels/full_biy_LEVELS.json')
var data3 = require('../json_levels/search_biy_LEVELS.json')


let possActions = ["space", "right", "up", "left", "down"];

let counter = 0;



// NEXT ITERATION STEP FOR SOLVING
function iterSolve(init_state){
    //test any of the known solutions
    // PERFORM ITERATIVE CALCULATIONS HERE //

    console.log(solutions.length);
    var result = [];

    if (counter < solutions.length) {
        solution = solutions[counter]["solution"];

        solution.split('').map(letter => {
            if (letter == 'r') result.push("right");
            if (letter == 'l') result.push("left");
            if (letter == 'u') result.push("up");
            if (letter == 'd') result.push("down");
            if (letter == 's') result.push("space");
        });
        console.log(result)
        counter += 1;
    }

    //return a sequence of actions or empty list
    return result;
}



// VISIBLE FUNCTION FOR OTHER JS FILES (NODEJS)
module.exports = {
    step : function(init_state){return iterSolve(init_state)},		// iterative step function (returns solution as list of steps from poss_actions or empty list)
    init : function(init_state){
        counter = 0;
        solutions = data1.levels.concat(data2.levels).concat(data3.levels);
    },							// initializing function here
    best_sol : function(){return [];}				//returns closest solution in case of timeout
}


