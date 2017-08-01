#!/usr/bin/env python
# coding=utf-8
      
''' Learn anything anywhere! '''

test = False

import json
import os
import re
import random
import signal
import sys
import termios
import tty
from os.path import join, isfile

devider = '|'
class bcolors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_green(string):
    print '%s%s%s' % (bcolors.GREEN, string, bcolors.ENDC)

def print_red(string):
    print '%s%s%s' % (bcolors.RED, string, bcolors.ENDC)

def print_bold(string):
    print '%s%s%s' % (bcolors.BOLD, string, bcolors.ENDC)

def clear():
    os.system('clear')

def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch
class AlarmException(Exception):
    pass

def alarmHandler(signum, frame):
    raise AlarmException
def nonBlockingRawInput(prompt='', timeout=100000):
    signal.signal(signal.SIGALRM, alarmHandler)
    signal.alarm(timeout)
    try:
        text = getch()
        signal.alarm(0)
        return text
    except AlarmException:
        pass
    signal.signal(signal.SIGALRM, signal.SIG_IGN)
    return '0'


def print_menu(index, lessons):
  clear()
  print 'Choose subject:'
  print '---------------'
  dir_pos = 0
  for lesson in lessons:
    lesson_name = lesson.replace('.json', '').split('_')
    name_cap = reduce(lambda x, y: '%s %s' % (x.capitalize(), y.capitalize()), lesson_name)
    if index == dir_pos:
      print_bold(name_cap)
    else:
      print name_cap
    dir_pos += 1

def handle_input(index, size):
    action = False
    quit = False
    input = getch()
    if input == 'd':
      index += 1
    elif input == 's':
      index -= 1
    elif input == 'a':
      action = True
    elif input == 'q':
      quit = True
    elif input == '\x03':
      sys.exit(1)
    if index >= size:
      index = 0
    elif index < 0:
      index = size - 1
    return (index, action, quit)

def question(word, dictionary, sec):
    
    os.system('clear')
    print 'English word for: %s' % word[1]
    alt = []
    for entry in dictionary:
        if entry[0] != word[0]:
            alt.append(entry[0])

    alt = random.sample(alt, 2)
    alt.append(word[0])
    random.shuffle(alt)

    print devider + bcolors.BLUE + alt[0] + bcolors.ENDC + devider + '\t' + devider + bcolors.HEADER + alt[1] + bcolors.ENDC + devider + '\t' + devider + bcolors.RED + alt[2] + bcolors.ENDC + devider
    svar = nonBlockingRawInput('Your answer: ', sec)
    if svar == 'a':
        svar = alt[0]
    elif svar == 's':
        svar = alt[1]
    elif svar == 'd':
        svar = alt[2]

    if svar == word[0]:
        print_green('Correct!')
        answer = True
    else:
        print_red('Wrong!')
        answer = False
    return answer

def start_stage(stage_id, stage, dic):
  choices = ['Practice', 'Practice revers']
  index = 0
  while True:
    os.system('clear')
    print "Stage: " + str(stage_id)
    i = 0
    for choice in choices:
      if i == index:
        print_bold(choice)
      else:
        print choice
      i = i+1

    (index, action, quit) = handle_input(index, len(choices))
    if action:
      if (index == 0):
        questions = dic[stage[0]:stage[1]]

        bigdict = []
        for i in range(0, 1):
          iteration = list(questions)
          random.shuffle(questions)
          bigdict += iteration

        correct_answ = 0
        for word in bigdict:
          if question(word, questions, 4000):
              correct_answ += 1
          raw_input('Press enter to try the next word')
        print 'You scored %s/%s, percent %s' % (correct_answ, len(bigdict), float(correct_answ) / float(len(bigdict)))
    if quit:
      break

def enter_lesson(lesson_file):
  clear()
  index = 0
  lesson = json.loads(open(lesson_file).read())
  dic = lesson["words"]
  lesson_size = 6
  multiplier = 5
  stages = []
  for i in range(0, len(dic) / lesson_size):
    start = i * lesson_size
    end = (i + 1) * lesson_size
    stages.append((start, end))
    back = i 
    while back > 0:
      stages.append((back*lesson_size - lesson_size, end))
      back -= 1
    
  if test:
      start_stage(0, stages[0], dic)
  while True:
    os.system('clear')
    print 'Lesson: %s' % lesson_file
    for i in range(len(stages)):
      text = "%d: %s - %s" % (i, dic[stages[i][0]][1], dic[stages[i][1] - 1][1]) 
      if i == index:
        print_bold(text)
      else:
        print text
    (index, action, quit) = handle_input(index, len(stages))
    if action:
      start_stage(i, stages[i], dic)
    if quit:
      break

def main():
  index = 0
  data_path = 'lessons'
  lessons = [lesson for lesson in os.listdir(data_path) if isfile(join(data_path, lesson)) and lesson.endswith('.json')]
  if test:
    enter_lesson(join(data_path, lessons[0]))
  while True:
    print_menu(index, lessons)
    (index, action, quit) = handle_input(index, len(lessons))
    if action:
      enter_lesson(join(data_path, lessons[index]))
    if quit:
        break

if __name__ == '__main__':
  main()
