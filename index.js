class TicTacToe {
	constructor(train_ai) {
		this.currentPlayer = 'x';
		this.board = document.querySelectorAll('.cell');
		this.gameInfo = document.getElementById('gameInfo');
		this.change_turn = document.getElementById('change_turn');
		this.train_ai = train_ai;
		resetGame();
	}

	get_available_moves() {
		const cells = document.querySelectorAll('.cell');
		return Array.from(cells).filter(cell => !cell.classList.contains('x') && !cell.classList.contains('o'));
	}

	winner() {
		const cells = this.board;
		if (this.get_available_moves().length === 0) {
			return 'draw';
		}
		for (var i=0; i<9; i+=3) {
			if (cells[i].classList.contains('x') && cells[i+1].classList.contains('x') && cells[i+2].classList.contains('x')) {
				return 'x';
			}
			if (cells[i].classList.contains('o') && cells[i+1].classList.contains('o') && cells[i+2].classList.contains('o')) {
				return 'o';
			}
		}
		for (var i=0; i<3; i++) {
			if (cells[i].classList.contains('x') && cells[i+3].classList.contains('x') && cells[i+6].classList.contains('x')) {
				return 'x';
			}
			if (cells[i].classList.contains('o') && cells[i+3].classList.contains('o') && cells[i+6].classList.contains('o')) {
				return 'o';
			}
		}
		if (cells[0].classList.contains('x') && cells[4].classList.contains('x') && cells[8].classList.contains('x')) {
			return 'x';
		}
		if (cells[2].classList.contains('x') && cells[4].classList.contains('x') && cells[6].classList.contains('x')) {
			return 'x';
		}
		if (cells[0].classList.contains('o') && cells[4].classList.contains('o') && cells[8].classList.contains('o')) {
			return 'o';
		}
		if (cells[2].classList.contains('o') && cells[4].classList.contains('o') && cells[6].classList.contains('o')) {
			return 'o';
		}
		return null;
	}

	winner_change_cell() {
		return this.train_ai.cell_with_higher_rank(this, true)[1];
	}

	randomCell() {
		return this.get_available_moves()[Math.floor(Math.random() * this.get_available_moves().length)];
	}

	change_player() {
		this.currentPlayer = this.currentPlayer === 'x' ? 'o' : 'x';
	}

	move(cell) {
		if(!cell) {
			if(this.train_ai) {
				cell = this.winner_change_cell()
			}
			 if(!cell) {
				cell = this.randomCell();
			}
		}
		cell.classList.add(this.currentPlayer);
		this.change_player();
		return this.winner();
	}

	raw_board_data() {
		return Array.from(this.board).map(cell => cell.classList.contains('x') ? 'x' : cell.classList.contains('o') ? 'o' : 'none');
	}
}

class TicTacToeAI {
	constructor(training_count=10000) {
		this.training_count = training_count;
		this.learning_rate = 0.5;
		this.q_table = [];
	}

	get_q_table(key) {
		if(this.q_table[key]) return this.q_table[key];
		return 0;
	}

	update_q_table(key, old_q_value, reward, next_reward) {
		this.q_table[key] = old_q_value + this.learning_rate * (reward + next_reward - old_q_value);
	}

	clone_new_move(new_train, index) {
		var board = new_train.raw_board_data()
		board[index] = new_train.currentPlayer;
		return board.join(",");
	}

	cell_with_higher_rank(new_train, only_max=false) {
		var original_data = new_train.raw_board_data();
		var rank = -999999;
		var new_moves = []
		var max_cell;
		for(var i=0; i<9; i++) {
			if(original_data[i] == "none") {
				var new_board = this.clone_new_move(new_train, i);
				if(this.q_table[new_board] >= rank) {
					new_moves.push(i);
					rank = this.q_table[new_board];
					max_cell = i;
				}
			}
		}

		if (only_max) {
			return [rank, new_train.board[max_cell]];
		}
		return [rank, new_train.board[new_moves[Math.floor(Math.random() * new_moves.length)]]];
	}

	run_loop = async () => { // ✅ Use arrow function to keep `this`
        var new_count = this.training_count;
		window.training = true;
		
		document.getElementById('board').style.pointerEvents = "none";
		document.getElementById('restart').style.pointerEvents = "none";
		document.getElementById('change_turn').style.pointerEvents = "none";
        while (new_count >= 0) {
            let new_train = new TicTacToe();
            new_train.currentPlayer = ['x', 'o'][Math.floor(Math.random() * 2)];
            new_count -= 1;
            var old_data = {};

            while (new_train.winner() == null) {
				var current_state = new_train.raw_board_data().join(",");
                old_data[new_train.currentPlayer] = current_state;
                var old_q_value = this.get_q_table(current_state);

                new_train.move(this.cell_with_higher_rank(new_train)[1]);
                var new_q_value = this.cell_with_higher_rank(new_train, true)[0];

                if (new_train.winner() == 'x' || new_train.winner() == 'o') {
                    this.update_q_table(current_state, old_q_value, 1, new_q_value);

                    this.update_q_table(old_data[new_train.currentPlayer], old_q_value, -1, new_q_value);
                    break;
                }else if (new_train.winner() == 'draw') {
					this.update_q_table(current_state, old_q_value, -1, new_q_value);
                    this.update_q_table(old_data[new_train.currentPlayer], old_q_value, -1, new_q_value);
                    break;
                }

                // ✅ Add a 100ms delay in the loop
                await new Promise(resolve => setTimeout(resolve, 0.0001));
            }

            updateProgress(this.training_count - new_count, this.training_count);
			if (!window.training) break;
        }
		updateProgress(this.training_count, this.training_count);
		delete window.training;
		resetGame();
		console.log(this.q_table);
		game = new TicTacToe(this);
    }

	train() {
		this.run_loop();
	}
}

function updateProgress(count, total_count) {
	const progressBar = document.getElementById('gameProgress');
	const progressPercent = parseInt((count / total_count) * 100);
	progressBar.style.width = progressPercent + '%';
}

function makeMove(cell) {
	game_state = game.move(cell);
	if (game_state && game_state != "draw") {
		game.gameInfo.textContent = `Player ${game.currentPlayer.toUpperCase()} wins!`;
		document.getElementById('board').style.pointerEvents = "none";
		return;
	}
	game_state = game.move();
	if (game_state && game_state != "draw") {
		game.gameInfo.textContent = `Player ${game.currentPlayer.toUpperCase()} wins!`;
		document.getElementById('board').style.pointerEvents = "none";
		return;
	}
	if (game_state == "draw") {
		game.gameInfo.textContent = `Draw`;
		document.getElementById('board').style.pointerEvents = "none";
	}
}

function resetGame() {
	const cells = document.querySelectorAll('.cell');
	cells.forEach(cell => {
		cell.classList.remove('x', 'o');
	});
	if(!window.training){
		document.getElementById('board').style.pointerEvents = "";
		document.getElementById('restart').style.pointerEvents = "";
		document.getElementById('change_turn').style.pointerEvents = "";
	}
}

function whoseFirstTurn() {
	if (game.currentPlayer === 'x') {
		game.gameInfo.textContent = 'You Play o';
		game.change_turn.textContent = 'o';
		game.change_player();
	} else {
		game.gameInfo.textContent = 'You Play x';
		game.change_turn.textContent = 'x';
		game.change_player()
	}
}
var game = new TicTacToe();
function TrainAI() {
	if (!window.training) {
		var train_ai = new TicTacToeAI();
		document.getElementById('train_btn').textContent = "STOP";
		train_ai.train();
	} else {
		delete window.training;
		document.getElementById('train_btn').textContent = "Train AI";
	}
}