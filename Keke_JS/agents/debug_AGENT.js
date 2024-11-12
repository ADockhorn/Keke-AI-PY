// BABA IS Y'ALL SOLVER - BLANK TEMPLATE
// Version 1.0
// Code by Milk 


//get imports (NODEJS)
var simjs = require('../js/simulation')					//access the game states and simulation

let possActions = ["space", "right", "up", "left", "down"];
let counter = 0;
var currentGamestate = simjs.getGamestate();


// NEXT ITERATION STEP FOR SOLVING
function iterSolve(init_state){
	// PERFORM ITERATIVE CALCULATIONS HERE //
	
	if(counter < 1)
	{

	
	let print = JSON.stringify(currentGamestate);


	const fs = require('fs');
	fs.appendFile("../../debug", print, (err) => {
      
    // In case of a error throw err.
    if (err) throw err;
	});

	counter += 1;
	}
	
	//return a sequence of actions or empty list
	return [];
}



// VISIBLE FUNCTION FOR OTHER JS FILES (NODEJS)
module.exports = {
	step : function(init_state){return iterSolve(init_state)},		// iterative step function (returns solution as list of steps from poss_actions or empty list)
	init : function(init_state){},							// initializing function here
	best_sol : function(){return [];}				//returns closest solution in case of timeout
}


