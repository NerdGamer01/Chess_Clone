from move_gen import generate_legal_moves
from copy import deepcopy
import threading


class AI(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.board = None
        self.move = None

    def run(self):
        print('START')
        self.move = self.minimax(self.board, 4, float('-inf'), float('inf'), [])[1][0]
        print('DONE')

    # recursive function for minimax algorithm with alpha beta pruning
    def minimax(self, board, depth, alpha, beta, previous_moves):
        if depth == 0:
            return (board.evaluation(), previous_moves)

        moves = generate_legal_moves(board)

        if board.turn == 'Black':
            maxEval = float('-inf')

            if len(moves) == 0:
                return (maxEval, previous_moves)

            for m in moves:
                new_board = deepcopy(board)
                new_board.apply_move(m)
                new_moves = deepcopy(previous_moves)
                new_moves.append(m)

                result = self.minimax(new_board, depth - 1, alpha, beta, new_moves)

                if result[0] > maxEval:
                    maxEval = result[0]
                    final_moves = result[1]

                alpha = max(alpha, result[0])

                if beta <= alpha:
                    break

            return (maxEval, final_moves)

        else:
            minEval = float('inf')

            if len(moves) == 0:
                return (minEval, previous_moves)

            for m in moves:
                new_board = deepcopy(board)
                new_board.apply_move(m)
                new_moves = deepcopy(previous_moves)
                new_moves.append(m)

                result = self.minimax(new_board, depth - 1, alpha, beta, new_moves)

                if result[0] < minEval:
                    minEval = result[0]
                    final_moves = result[1]

                beta = min(beta, result[0])

                if beta <= alpha:
                    break

            return (minEval, final_moves)