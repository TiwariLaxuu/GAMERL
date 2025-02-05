from dash import Dash, dcc, html, Input, Output
import dash
import time 

# Initialize the app
app = Dash(__name__)

# The initial game board (7x7 grid)
board = [['' for _ in range(7)] for _ in range(7)]

# Starting player (Black starts)
current_player = 'Black'  # Can be 'Black' or 'White'
black_moves = 0  # Counter to keep track of Black's moves
white_moves = 0  # Counter to keep track of White's moves
black_move_placement = 0
white_move_placement = 0
max_move_in_placement = 2 
max_moves = 24  # Each player can place 24 pieces on the board (total of 48 pieces)
game_over = False  # Game over flag to prevent further moves
captured_pieces = {'Black': 0, 'White': 0}  # Captured pieces counter for each player
selected_piece = None  # To store the selected piece to move
phase = 'Placement'  # 'Placement' or 'Movement' phase

# Function to generate the board layout
def generate_board_layout():
    return [
        html.Div(
            [
                html.Button(
                    children=[
                        html.Div(
                            style={
                                'width': '40px', 'height': '40px',
                                'borderRadius': '50%', 'backgroundColor': 'black' if board[i][j] == 'B' else ('white' if board[i][j] == 'W' else 'transparent'),
                                'border': '2px solid black' if board[i][j] else 'none',
                                'margin': 'auto'
                            }
                        )
                    ],
                    id={'type': 'cell', 'index': f'{i},{j}'}, 
                    n_clicks=0, 
                    style={
                        'width': '60px', 'height': '60px',
                        'fontSize': '20px', 'textAlign': 'center',
                        'backgroundColor': 'lightgrey', 'border': '1px solid black'
                    }
                )
                for j in range(7)
            ], style={'display': 'flex'}
        ) for i in range(7)
    ]

# Function to check for captures on the board
def check_for_captures(board, current_players, i, j):
    current_player = 'B' if current_players == 'Black' else 'W'
    opponent = 'W' if current_player == 'B' else 'B'
    captured = []
    captured_count = 0
    print('i:', i, 'j:', j, current_player)
    # Check for horizontal captures
    # for i in range(7):
    #     for j in range(5):  # Only need to check up to index 5 for horizontal captures
    try:
        if board[i][j] == current_player and board[i][j+1] == opponent and board[i][j+2] == current_player and i < 7 and j+2 <= 7 and i > 0 and j+2 > 0:
            captured_pieces[current_players] += 1
            captured.append((i, j+1))  # Capture the piece at (i, j+1)
            captured_count += 1
            board[i][j+1] = ''  # Remove the captured piece
    except IndexError:
        pass
    try:
        if board[i][j] == current_player and board[i+1][j] == opponent and board[i+2][j] == current_player and i+2 <= 7 and j < 7 and i+2 > 0 and j > 0:
            captured_pieces[current_players] += 1
            captured.append((i+1, j))  # Capture the piece at (i+1, j)
            captured_count += 1
            board[i+1][j] = ''
    except IndexError:
        pass

    try:
        if board[i][j] == current_player and board[i][j-1] == opponent and board[i][j-2] == current_player and i < 7 and j-2 < 7 and i > 0 and j-2 > 0:
            captured_pieces[current_players] += 1
            captured.append((i, j-1))
            captured_count += 1
            board[i][j-1] = ''
    except IndexError:
        pass


    try:
        if board[i][j] == current_player and board[i-1][j] == opponent and board[i-2][j] == current_player and i-2 < 7 and j < 7 and i-2 > 0 and j > 0:
            captured_pieces[current_players] += 1
            captured.append((i-1, j))
            captured_count += 1
            board[i-1][j] = ''
    except IndexError:
        pass

    return board, captured_count
# Function to check for available moves in Placement Phase (all empty spaces except the center)
def check_available_moves_placement(board):
    available_moves = []
    for i in range(7):
        for j in range(7):
            if (i != 3 or j != 3) and board[i][j] == '':  # All empty spaces except the center
                available_moves.append((i, j))
    return available_moves

# Function to check for available moves for the current player
def check_available_moves_movement(board, current_player):
    available_moves = []
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Up, Down, Left, Right
    for i in range(7):
        for j in range(7):
            print('available moves for current_player:', current_player)
            if board[i][j] == current_player[0]:  # If it's the current player's piece
                # Check if any adjacent space is empty
                for di, dj in directions:
                    ni, nj = i + di, j + dj
                    print('ni:', ni, 'nj:', nj)
                    if 0 <= ni < 7 and 0 <= nj < 7 and board[ni][nj] == '':
                        available_moves.append((i, j))  # The piece at (i, j) has a valid move
                        print('available_moves:', available_moves)
                        break
    return available_moves

def check_for_game_over(board, current_player, captured_pieces):
    if current_player == 'Black':
        available_moves = check_available_moves_movement(board, current_player)
        if not available_moves:  # No available moves for Black
            winner = 'White' if captured_pieces['White'] > captured_pieces['Black'] else 'Black'
            return True, winner
    elif current_player == 'White':
        available_moves = check_available_moves_movement(board, current_player)
        if not available_moves:  # No available moves for White
            winner = 'Black' if captured_pieces['Black'] > captured_pieces['White'] else 'White'
            return True, winner

    return False, None 

# Create layout for the app
app.layout = html.Div(
    children=[
        html.H1("SEEGA Game", style={'textAlign': 'center'}),
        html.H2('Players: Black and White'),
        html.Div(id='game-board', children=generate_board_layout()),  # Displaying game board
        html.Div(id='game-status', children=f"Current Player: {current_player}, Phase: {phase}"),  # Displaying current player and phase
        html.Div(id='captured-status', children=f"Black Captured: {captured_pieces['Black']} | White Captured: {captured_pieces['White']}"),  # Display captured pieces
    ]
)

# Callback to update the board when a cell is clicked
@app.callback(
    [Output('game-board', 'children'),
     Output('game-status', 'children'),
     Output('captured-status', 'children')],
    [Input({'type': 'cell', 'index': dash.ALL}, 'n_clicks')],
)
def update_board(n_clicks):
    global board, current_player, black_moves, white_moves, black_move_placement, white_move_placement, max_moves, game_over, captured_pieces, selected_piece, phase, max_move_in_placement

    if game_over:
        return generate_board_layout(), "Game Over! Board is full.", f"Black Captured: {captured_pieces['Black']} | White Captured: {captured_pieces['White']}"

    if not any(n_clicks):  # If no button has been clicked yet
        return generate_board_layout(), f"Current Player: {current_player}, Phase: {phase}", f"Black Captured: {captured_pieces['Black']} | White Captured: {captured_pieces['White']}"

    updated_board = [row[:] for row in board]  # Copy the current board
    clicked_index = None

    for idx, clicks in enumerate(n_clicks):
        if clicks > 0:  # If the button is clicked
            i, j = divmod(idx, 7)  # Get the row and column index from the flat index

            if phase == 'Placement':
                # Handle piece placement phase (Black and White alternate placing pieces)
                if updated_board[i][j] == '' and (i != 3 or j != 3):  # Prevent center (3,3) placement
                    if current_player == 'Black' and black_moves < max_moves:
                        updated_board[i][j] = 'B'  # Place Black piece
                        black_moves += 1
                        black_move_placement += 1
                    elif current_player == 'White' and white_moves < max_moves:
                        updated_board[i][j] = 'W'  # Place White piece
                        white_moves += 1
                        white_move_placement += 1
                    # Switch players' turns after placing 2 pieces

                    if black_move_placement == max_move_in_placement:
                        current_player = 'White'
                        black_move_placement = 0  # Reset Black's move counter

                    if white_move_placement == max_move_in_placement:
                        current_player = 'Black'
                        white_move_placement = 0  # Reset White's move counter
                    # Check if all pieces are placed
                    if black_moves == max_moves and white_moves == max_moves:
                        phase = 'Movement'  # Switch to movement phase

            elif phase == 'Movement':
                # Handle piece movement phase
                if updated_board[i][j] == '' and selected_piece:  # If clicked on an empty space and a piece is selected
                    selected_i, selected_j = selected_piece
                    updated_board[i][j] = updated_board[selected_i][selected_j]  # Move the piece
                    updated_board[selected_i][selected_j] = ''  # Clear the initial position
                    time.sleep(5)
                    # Check for captures after the move
                    updated_board, captured_count = check_for_captures(updated_board, current_player, i, j)
                    print('updated_board:', updated_board)
                    # for piece in captured:
                    #     captured_pieces[current_player] += 1
                    #     updated_board[piece[0]][piece[1]] = ''  # Remove captured piece

                    # Switch player turn after a move
                    if captured_count > 1:
                        current_player = current_player
                    else:
                        current_player = 'White' if current_player == 'Black' else 'Black'
                    selected_piece = None  # Reset selected piece

                elif updated_board[i][j] == current_player[0]:  # If the clicked cell contains the current player's piece
                    # Select the piece to move
                    available_moves = check_available_moves_movement(updated_board, current_player[0])
                    if (i, j) in available_moves:
                        selected_piece = (i, j)
                        return generate_board_layout(), f"Current Player: {current_player}, Select a destination", f"Black Captured: {captured_pieces['Black']} | White Captured: {captured_pieces['White']}"

    # Check if there are any available moves for Black
    
                available_moves = check_available_moves_movement(updated_board, current_player)
                game_over_flag, winner = check_for_game_over(updated_board, current_player, captured_pieces)
                if not available_moves and game_over_flag:  # No available moves for Black, game over
                    game_over = True
                    winner = 'White' if captured_pieces['White'] > captured_pieces['Black'] else 'Black'
                    return generate_board_layout(), f"Game Over! {winner} wins!", f"Black Captured: {captured_pieces['Black']} | White Captured: {captured_pieces['White']}"

    # Update the board layout with the new values
    board = updated_board
    return generate_board_layout(), f"Current Player: {current_player}, Phase: {phase}", f"Black Captured: {captured_pieces['Black']} | White Captured: {captured_pieces['White']}"

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
