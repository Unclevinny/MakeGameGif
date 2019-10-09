import chess
import chess.engine
import chess.pgn
import os
import imageio
import png
from PIL import Image, ImageDraw, ImageFont

CANVAS_SIZE = 300
UNIT = CANVAS_SIZE/22
GAP = int(0.30 * UNIT)
MID = int(CANVAS_SIZE / 2)
Y_SEP = int(1.5 * UNIT) # this is the gap between B & W, to allow for KQRBNP text
REPETITIONS = 30 # number of times to repeat final frame
    
def get_fens(game):
    fen_list = []
    board = game.board()
    for move in game.mainline_moves():
        board.push(move)
        fen_list.append(board.fen())
    return fen_list
    

def find_pieces(fen):
    # output = count of [K, Q, R, B, N, P, k, q, r, b, n, p]
    fen_list = fen.split()
    piece_types = ['K', 'Q', 'R', 'B', 'N', 'P']
    piece_list = []
    for piece in piece_types:
        new_count = []
        new_count.append(fen_list[0].count(piece))
        piece_list += new_count
    for piece in piece_types:
        piece_list.append(fen_list[0].count(piece.lower()))
    return piece_list
    
    
def get_rect(type, is_present, prev_x2): # input will be 
                             # type = (0, 1, 2, or 11), 
                             # is_present = 1 or 0 
                             # prev_x1 = some value
    # Note: if number of queens, rooks, increases beyond the normal 'max' of 1 or 2, deal with it!
    # print('type,is_p,prev_x1: ', type, is_present, prev_x2)
    piece_heights = [1,9,5,3.5,3,1,1,9,5,3.5,3,1]
    result_rect = []
    
    # slots = buffer*1 + (1+1+2+2+2+8) + 0.3*1*17 =~ 21

    buffer = int(UNIT) # could change later

    unit = int(UNIT)
    
    if type > 5:
        parity = 1
    else:
        parity = -1
    
    if prev_x2 == 0:
        x1 = buffer
    else:
        x1 = prev_x2 + GAP
    x2 = x1 + unit
    y1 = MID + parity*Y_SEP/2
    y2 = MID + parity*Y_SEP/2 + is_present*parity*piece_heights[type]*unit
    result_rect.append(x1)  
    result_rect.append(y1)  
    result_rect.append(x2)  
    result_rect.append(y2)  
    
    return result_rect

    
def get_piece_lists(pgn_location):
    pgn = open(pgn_location)
    list_of_piece_lists = []
    finished = False
    while 1 != 0:
        next_game = chess.pgn.read_game(pgn)
        if (next_game == None):
            break
        white_player = next_game.headers["White"]
        black_player = next_game.headers["Black"]
        result = next_game.headers["Result"]
        # print('White, black: ', white_player, black_player)
        pieces_list = []
        fen_list = get_fens(next_game)
        for fen in fen_list:
            pieces_list.append(find_pieces(fen))
        ret_tuple = (white_player, black_player, result, pieces_list)
        list_of_piece_lists.append(ret_tuple)
    return list_of_piece_lists
            

def make_PNG_for_move(move, move_num, max_num, white_player, black_player, result=None):
    freeze = False
    if move_num == max_num:
        freeze = True
        
    init_piece_count =  [1, 1, 2, 2, 2, 8, 1, 1, 2, 2, 2, 8]
    pieces_count =      move
    
    canvas = (CANVAS_SIZE, CANVAS_SIZE)

    white_color = '#fafaf7'
    black_color = '#0a0a00'
    grey_color = '#a9bed6'
    dk_grey_color = '#425266'
    background = '#4c79c2'

    # background
    im = Image.new('RGBA', canvas, background)
    draw = ImageDraw.Draw(im)
    
    # draw rectangles
    # TODO: Handle creation of additional queens, etc
    font_size = 15
    font_size_sm = 15
    font_size_lg = 22
    font_treb = ImageFont.truetype("trebuc.ttf", font_size)
    font_treb_sm = ImageFont.truetype("trebucit.ttf", font_size_sm)
    font_treb_lg = ImageFont.truetype("trebucbd.ttf", font_size_lg)
    font_cour_lg = ImageFont.truetype("courbd.ttf", font_size_lg)
    experiment = font_cour_lg.getsize(result)

    
    # add pie chart
    box_x = CANVAS_SIZE - 2.5 * UNIT
    box_y = 0 + .5 * UNIT
    end_angle = 360*move_num/max_num
    draw.pieslice((box_x, box_y, box_x + 2* UNIT, box_y + 2 * UNIT), 0, end_angle, fill=white_color, outline=grey_color, width = 1)
    # add move number
    draw.text((box_x + UNIT/2, box_y + UNIT/4), repr(move_num//2), font=font_treb_sm, fill=black_color)
    # add player names
    if len(white_player) > 20:
        white_player = white_player[0:15] + '...'
    if len(black_player) > 20:
        black_player = black_player[0:15] + '...'        
    player_label = white_player + ' v. ' + black_player
    player_dim = font_treb_sm.getsize(player_label)
    player_x = CANVAS_SIZE - 3*UNIT - player_dim[0]
    player_y = 0.5 * UNIT
    draw.text((player_x, player_y), player_label, font=font_treb_sm, fill=dk_grey_color)
    
    # add result
    if freeze:
        if result == '1-0':
            result_color = white_color
        elif result == '0-1':
            result_color = black_color
        else:
            result_color = grey_color
        result_dim = font_cour_lg.getsize(result)
        result_x = CANVAS_SIZE - 3*UNIT - result_dim[0]
        result_y = 1.5 * UNIT
        draw.text((result_x, result_y), result, font=font_cour_lg, fill=result_color)
    
    for piece_type, max_piece_count in enumerate(init_piece_count):

        if piece_type == 0 or piece_type == 6:
            x2 = 0
        actual_count = pieces_count[piece_type]
        if actual_count > max_piece_count:
            max_piece_count = actual_count
        for possible_piece_count in range(0, max_piece_count):
            if actual_count > 0:
                rect = get_rect(piece_type, 1, x2)
            else:
                rect = get_rect(piece_type, 0, x2)
            if piece_type > 5:
                color = black_color
            else:
                color = white_color
            x1 = rect[0]
            y1 = rect[1]
            x2 = rect[2]
            y2 = rect[3]
            draw.rectangle([x1, y1, x2, y2], fill=color)
            font_y = MID-(3*(Y_SEP-font_size) / 2)
            piece_label=''
            if (piece_type in (0,6)):
                piece_label='K'
            if (piece_type in (1,7)):
                piece_label='Q'
            if (piece_type in (2,8)):
                piece_label='R'
            if (piece_type in (3,9)):
                piece_label='B'
            if (piece_type in (4,10)):
                piece_label='N'
            if (piece_type in (5,11)):
                piece_label='P'
            draw.text((x1, font_y), piece_label, font=font_treb, fill=grey_color)
            actual_count -= 1

    if freeze:
        for j in range(move_num, move_num + REPETITIONS):
            savename = 'Game_Move_' + repr(j) + '.png'

            if os.path.exists(savename):
                os.remove(savename)
            im.save(savename)
    else:        
        savename = 'Game_Move_' + repr(move_num) + '.png'
        if os.path.exists(savename):
            os.remove(savename)

        im.save(savename)


def make_GIF_from_PNGs(max_move, game_num):
    images = []
    for x in range(1,max_move):
        thisfilename = 'Game_Move_' + repr(x) + '.png'
        f = open(thisfilename, 'rb')
        images.append(imageio.imread(thisfilename))
        # Clean up temp files
        os.remove(thisfilename)
    imageio.mimsave('Game' + repr(game_num) + '.gif', images)    


def main():

    # Get list of pieces for each move in a game
    pgn_filename = 'AFewGames.pgn'
    list_of_piece_lists = get_piece_lists(pgn_filename)
    for game_count, game_tuple in enumerate(list_of_piece_lists):
        white_player = game_tuple[0]
        black_player = game_tuple[1]
        result = game_tuple[2]
        game = game_tuple[3]

        print("starting game #", repr(game_count), ', result =', result)
        max_move = len(game)
        move_num = 0
        # Make PNGs for each move in the game
        for move in game:
            move_num += 1
            make_PNG_for_move(move, move_num, max_move, white_player, black_player, result)
        gif_length = max_move + REPETITIONS
        # Create GIF
        make_GIF_from_PNGs(gif_length, game_count)
    

if __name__ == "__main__":
    main()

