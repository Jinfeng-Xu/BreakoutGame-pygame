'''
功能：使用pyGame实现一个简单的打砖块游戏
@author: Jinfeng Xu
'''

import pygame, sys, time, random  # @UnusedImport
from pygame.locals import *  # @UnusedWildImport
import pygame.freetype

import easygui as g
import pickle

'-------------- --账号登录---------------------'
n = 0
user = 0
list1 = ['*用户名:', '*真实姓名:', '*输入密码:', '*再次输入:', 'Email:', 'QQ:', '电话:']  # 初始化计量参数

with open('userlist.pkl', 'rb') as hf:
    user_list = pickle.load(hf)  # 导入，初次使用的可以先建立一个字典保存为userlist.pkl

while n != 1:
    [name, password] = g.multpasswordbox(msg='请输入用户名和密码', title=' 账号登录', fields=('用户名', '密码'), values=())
    if name in user_list:
        if user_list[name] == password:
            g.msgbox(msg='登录成功', title='账号登录 ', ok_button='确定')
            n = 1
        else:
            g.msgbox(msg='密码不正确', title='账号登录 ', ok_button='返回')
    else:
        ser = g.buttonbox('账号不存在', choices=('重新输入', '注册新号', '退出程序'))
        if ser == '注册新号':
            while (user != 1):
                [nuser, nname, nmm1, nmm2, nemail, nqq, ntel] = g.multenterbox(msg='*为必填项，两次密码输入请一致', title='账号注册 ',
                                                                               fields=(list1))
                if nmm1 != nmm2:
                    g.msgbox(msg='两次输入的密码不一致', title='注册新号 ', ok_button='返回')
                elif nuser in user_list:
                    g.msgbox(msg='账号已存在', title='注册新号 ', ok_button='返回')
                elif nuser and nmm1 and nmm2 == 0:
                    g.msgbox(msg='必填项不能为空', title='注册新号 ', ok_button='返回')
                else:
                    user = 1
                    user_list[nuser] = nmm1
        elif ser == '退出程序':
            sys.exit()

'----------------------------------------------'
with open('userlist.pkl', 'wb') as hf:
    pickle.dump(user_list, hf)

# 一些关于窗口的常量定义
WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480

# 游戏状态常量定义
GAME_STATE_INIT = 0
GAME_STATE_START_LEVEL = 1
GAME_STATE_RUN = 2
GAME_STATE_GAMEOVER = 3
GAME_STATE_SHUTDOWN = 4
GAME_STATE_EXIT = 5

# 小球的常量定义
BALL_START_Y = (WINDOW_HEIGHT // 2)
BALL_SIZE = 4

# 挡板的常量定义
PADDLE_START_X = (WINDOW_WIDTH / 2 - 16)
PADDLE_START_Y = (WINDOW_HEIGHT - 32);
PADDLE_WIDTH = 32
PADDLE_HEIGHT = 8

# 砖块的常量定义
NUM_BLOCK_ROWS = 6
NUM_BLOCK_COLUMNS = 8
BLOCK_WIDTH = 64
BLOCK_HEIGHT = 16
BLOCK_ORIGIN_X = 8
BLOCK_ORIGIN_Y = 8
BLOCK_X_GAP = 80
BLOCK_Y_GAP = 32

# 一些颜色常量定义
BACKGROUND_COLOR = (0, 0, 0)
BALL_COLOR = (0, 0, 255)
PADDLE_COLOR = '#FFFF00'
BLOCK_COLOR = (255, 193, 193)
TEXT_COLOR = (255, 255, 255)

# 游戏的一些属性信息
TOTAL_LIFE = 5
FPS = 25


# 初始化砖块数组
def InitBlocks():
    # blocks = [[1] * NUM_BLOCK_COLUMNS] * NUM_BLOCK_ROWS
    blocks = []
    for i in range(NUM_BLOCK_ROWS):  # @UnusedVarialbe
        blocks.append([i + 1] * NUM_BLOCK_COLUMNS)
    return blocks


# 检测小球是否与挡板或者砖块碰撞
def ProcessBall(blocks, ball_x, ball_y, paddle):
    if (ball_y > WINDOW_HEIGHT // 2):
        if (ball_x + BALL_SIZE >= paddle['rect'].left and \
                ball_x - BALL_SIZE <= paddle['rect'].left + PADDLE_WIDTH and \
                ball_y + BALL_SIZE >= paddle['rect'].top and \
                ball_y - BALL_SIZE <= paddle['rect'].top + PADDLE_HEIGHT):
            return None


# 显示文字
def DrawText(text, font, surface, x, y):
    text_obj = font.render(text, 1, TEXT_COLOR)
    text_rect = text_obj.get_rect()
    text_rect.topleft = (x, y)
    surface.blit(text_obj, text_rect)


# 退出游戏
def Terminate():
    pygame.quit()
    sys.exit()


# 等待用户输入
def WaitForPlayerToPressKey():
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                Terminate()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    Terminate()
                return


# 游戏界面的初始化
pygame.init()
mainClock = pygame.time.Clock()

# 小球的位置和速度
ball_x = 0
ball_y = 0
ball_dx = 0
ball_dy = 0

# 挡板的运动控制
paddle_move_left = False
paddle_move_right = False

# 挡板的位置和颜色
paddle = {'rect': pygame.Rect(0, 0, PADDLE_WIDTH, PADDLE_HEIGHT),
          'color': PADDLE_COLOR}

# 游戏状态
game_state = GAME_STATE_INIT
blocks = []
life_left = TOTAL_LIFE
game_over = False
blocks_hit = 0
score = 0
level = 1

game_start_font = pygame.font.SysFont(None, 48)
game_over_font = pygame.font.SysFont(None, 48)
text_font = pygame.font.SysFont(None, 20)

game_over_sound = pygame.mixer.Sound('gameover.wav')
game_hit_sound = pygame.mixer.Sound('hit.wav')
pygame.mixer.music.load('background.mp3')

windowSurface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), 0, 32)
pygame.display.set_caption('打砖块')

DrawText('BreakOutGame', game_start_font, windowSurface,
         (WINDOW_WIDTH / 3), (WINDOW_HEIGHT / 3 + 50))
DrawText('Press any key to start.', game_start_font, windowSurface,
         (WINDOW_WIDTH / 3) - 60, (WINDOW_HEIGHT) / 3 + 100)
pygame.display.update()
WaitForPlayerToPressKey()

# 播放背景音乐
pygame.mixer.music.play(-1, 0.0)

# 游戏主循环
while True:
    # 事件监听
    for event in pygame.event.get():
        if event.type == QUIT:
            Terminate()
        if event.type == KEYDOWN:
            if event.key == K_LEFT:
                paddle_move_left = True
            if event.key == K_RIGHT:
                paddle_move_right = True
            if event.key == K_ESCAPE:
                Terminate()
        if event.type == KEYUP:
            if event.key == K_LEFT:
                paddle_move_left = False
            if event.key == K_RIGHT:
                paddle_move_right = False

    # 游戏控制流程
    if game_state == GAME_STATE_INIT:
        # 初始化游戏
        ball_x = random.randint(8, WINDOW_WIDTH - 8)
        ball_y = BALL_START_Y
        ball_dx = random.randint(-3, 4)
        ball_dy = random.randint(5, 8)

        paddle['rect'].left = PADDLE_START_X
        paddle['rect'].top = PADDLE_START_Y

        paddle_move_left = False
        paddle_move_right = False

        life_left = TOTAL_LIFE
        game_over = False
        blocks_hit = 0
        score = 0
        level = 1
        game_state = GAME_STATE_START_LEVEL
    elif game_state == GAME_STATE_START_LEVEL:
        # 新的一关
        blocks = InitBlocks()
        game_state = GAME_STATE_RUN
    elif game_state == GAME_STATE_RUN:
        # 游戏运行

        # 球的运动
        ball_x += ball_dx;
        ball_y += ball_dy;

        if ball_x > (WINDOW_WIDTH - BALL_SIZE) or ball_x < BALL_SIZE:
            ball_dx = -ball_dx
            ball_x += ball_dx;
        elif ball_y < BALL_SIZE:
            ball_dy = -ball_dy
            ball_y += ball_dy
        elif ball_y > WINDOW_HEIGHT - BALL_SIZE:
            if life_left == 0:
                game_state = GAME_STATE_GAMEOVER
            else:
                life_left -= 1
                # 初始化游戏
                ball_x = paddle['rect'].left + PADDLE_WIDTH // 2
                ball_y = BALL_START_Y
                ball_dx = random.randint(-4, 5)
                ball_dy = random.randint(6, 9)

        # 检测球是否与挡板碰撞
        if ball_y > WINDOW_HEIGHT // 2:
            if (ball_x + BALL_SIZE >= paddle['rect'].left and \
                    ball_x - BALL_SIZE <= paddle['rect'].left + PADDLE_WIDTH and \
                    ball_y + BALL_SIZE >= paddle['rect'].top and \
                    ball_y - BALL_SIZE <= paddle['rect'].top + PADDLE_HEIGHT):
                ball_dy = - ball_dy
                ball_y += ball_dy
                game_hit_sound.play()
                if paddle_move_left:
                    ball_dx -= random.randint(0, 3)
                elif paddle_move_right:
                    ball_dx += random.randint(0, 3)
                else:
                    ball_dx += random.randint(-1, 2)

        # 检测球是否与砖块碰撞
        cur_x = BLOCK_ORIGIN_X
        cur_y = BLOCK_ORIGIN_Y
        for row in range(NUM_BLOCK_ROWS):
            cur_x = BLOCK_ORIGIN_X
            for col in range(NUM_BLOCK_COLUMNS):
                if blocks[row][col] != 0:
                    if (ball_x + BALL_SIZE >= cur_x and \
                            ball_x - BALL_SIZE <= cur_x + BLOCK_WIDTH and \
                            ball_y + BALL_SIZE >= cur_y and \
                            ball_y - BALL_SIZE <= cur_y + BLOCK_HEIGHT):
                        blocks[row][col] = 0
                        blocks_hit += 1
                        ball_dy = -ball_dy
                        ball_dx += random.randint(-1, 2)
                        score += 5 * (level + abs(ball_dx))
                        game_hit_sound.play()
                cur_x += BLOCK_X_GAP
            cur_y += BLOCK_Y_GAP

        if blocks_hit == NUM_BLOCK_ROWS * NUM_BLOCK_COLUMNS:
            level += 1
            blocks_hit = 0
            score += 1000
            game_state = GAME_STATE_START_LEVEL

        # 挡板的运动
        if paddle_move_left:
            paddle['rect'].left -= 8
            if paddle['rect'].left < 0:
                paddle['rect'].left = 0
        if paddle_move_right:
            paddle['rect'].left += 8
            if paddle['rect'].left > WINDOW_WIDTH - PADDLE_WIDTH:
                paddle['rect'].left = WINDOW_WIDTH - PADDLE_WIDTH

        # 绘制过程
        windowSurface.fill(BACKGROUND_COLOR)
        # 绘制挡板
        pygame.draw.rect(windowSurface, paddle['color'], paddle['rect'])
        # 绘制小球
        pygame.draw.circle(windowSurface, BALL_COLOR, (ball_x, ball_y),
                           BALL_SIZE, 0)
        # 绘制砖块
        cur_x = BLOCK_ORIGIN_X
        cur_y = BLOCK_ORIGIN_Y
        for row in range(NUM_BLOCK_ROWS):
            cur_x = BLOCK_ORIGIN_X
            for col in range(NUM_BLOCK_COLUMNS):
                if blocks[row][col] != 0:
                    pygame.draw.rect(windowSurface, BLOCK_COLOR,
                                     (cur_x, cur_y, BLOCK_WIDTH, BLOCK_HEIGHT))
                cur_x += BLOCK_X_GAP
            cur_y += BLOCK_Y_GAP

        # 绘制文字描述信息
        message = 'Level: ' + str(level) + '    Life: ' + str(life_left) + '    Score: ' + str(score)
        DrawText(message, text_font, windowSurface, 8, (WINDOW_HEIGHT - 16))
    elif game_state == GAME_STATE_GAMEOVER:
        DrawText('GAME OVER', game_over_font, windowSurface,
                 (WINDOW_WIDTH / 3), (WINDOW_HEIGHT / 3))
        DrawText('Level: ' + str(level), game_over_font, windowSurface,
                 (WINDOW_WIDTH / 3) + 20, (WINDOW_HEIGHT / 3) + 50)
        DrawText('Score: ' + str(score), game_over_font, windowSurface,
                 (WINDOW_WIDTH / 3) + 20, (WINDOW_HEIGHT / 3) + 100)
        DrawText('Press any key to play again.', game_over_font, windowSurface,
                 (WINDOW_WIDTH / 3) - 80, (WINDOW_HEIGHT / 3) + 150)
        pygame.display.update()

        pygame.mixer.music.stop()
        game_over_sound.play()

        WaitForPlayerToPressKey()
        game_state = GAME_STATE_INIT
    elif game_state == GAME_STATE_SHUTDOWN:
        game_state = GAME_STATE_EXIT

    pygame.display.update()
    mainClock.tick(FPS + level * 2)
