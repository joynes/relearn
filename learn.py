#!/usr/bin/env python
# coding=utf-8
      
''' Learn anything anywhere! '''

test = False
ITERATIONS = 3
WRITE_ITERATIONS = 1
ITERATION_INDEX = 1
TIME_INDEX = 2

import json
import operator
import os
import re
import random
import signal
import sys
import termios
import tty
from os.path import join, isfile, expanduser

def get_sound_path(name):
  return join('data', name + '.m4a')

def play_sound(fil):
  path = 'data'
  if isfile(get_sound_path(fil[0])):
      os.system('afplay %s &' % get_sound_path(fil[0]))
  elif isfile(get_sound_path(fil[1])):
      os.system('afplay %s &' % get_sound_path(fil[1]))

def savepath():
  return join(expanduser('~'), '.learn')

def savefile(lesson_file):
  sfile = re.sub(r'(.*/)(.*).json', r'.\1\2_progress.json', lesson_file).replace('/', '_')
  return join(savepath(), sfile)

def wrongfile(lesson_file):
  sfile = re.sub(r'(.*/)(.*).json', r'.\1\2_wrong.json', lesson_file).replace('/', '_')
  return join(savepath(), sfile)


devider = '|'
class bcolors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_devider():
  print '----------------------------'

def print_selected(text):
  print_bold("%s %s" % (text, get_bold('<--')))

def print_title(title):
  print_devider()
  print_bold(title.upper())
  print_devider()
  print

def print_footer(extra=None):
  print
  print_devider()
  if extra:
    print extra
  print 's/d = up/down  a = choose  q = quit'
  print_devider()

def print_green(string):
  print '%s%s%s' % (bcolors.GREEN, string, bcolors.ENDC)

def get_red(string):
  return '%s%s%s' % (bcolors.RED, string, bcolors.ENDC)

def print_red(string):
  print get_red(string)

def get_bold(string):
  return '%s%s%s' % (bcolors.BOLD, string, bcolors.ENDC)

def print_bold(string):
  print get_bold(string)

def clear():
  os.system('clear')

def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
        if ch == '\x03':
          sys.exit(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

class AlarmException(Exception):
  pass

class QuitException(Exception):
  pass

def alarmHandler(signum, frame):
    raise AlarmException

def raw_input_timed(prompt='', timeout=100000):
    signal.signal(signal.SIGALRM, alarmHandler)
    signal.alarm(timeout)
    try:
        text = raw_input(prompt)
        signal.alarm(0)
        return text
    except AlarmException:
        pass
    signal.signal(signal.SIGALRM, signal.SIG_IGN)
    return '0'

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
  print_title('Choose subject:')
  dir_pos = 0
  for lesson in lessons:
    lesson_name = lesson.replace('.json', '').split('_')
    name_cap = ''
    for lesson_word in lesson_name:
      name_cap = name_cap + lesson_word.capitalize() + ' '

    if index == dir_pos:
      print_selected(name_cap)
    else:
      print name_cap
    dir_pos += 1
  print_footer()

def handle_input(index, size):
    action = None
    quit = False
    input = getch()
    if input == 'd':
      index += 1
    elif input == 's':
      index -= 1
    elif input in 'ae':
      action = input
    elif input == 'q':
      quit = True
    if index >= size:
      index = 0
    elif index < 0:
      index = size - 1
    return (index, action, quit)

def is_arabic(word):
    return ord(word[0]) > 0x600 and ord(word[0]) < 0x6FF

def question(word, dictionary, sec, lesson_file):
    
    alt = []
    for entry in dictionary:
        if entry[0] != word[0]:
            alt.append(entry[0])

    alt = random.sample(alt, 2)
    alt.append(word[0])
    random.shuffle(alt)

    clear()
    print 'Question: %s' % word[1]
    print
    print devider + bcolors.BLUE + alt[0] + bcolors.ENDC + devider + '\t' + devider + bcolors.HEADER + alt[1] + bcolors.ENDC + devider + '\t' + devider + bcolors.RED + alt[2] + bcolors.ENDC + devider
    inp = nonBlockingRawInput('Your answer: ', sec)
    svar = ''
    if inp == 'a':
        svar = alt[0]
    elif inp == 's':
        svar = alt[1]
    elif inp == 'd':
        svar = alt[2]
    elif inp == 'q':
      raise QuitException()

    if is_arabic(alt[0]):
      if inp == 'a':
        svar = alt[2]
      elif inp == 'd':
        svar = alt[0]

    if svar == word[0]:
        print_green('Correct!')
        answer = True
    else:
        print
        print_red('Wrong! Should be: %s' % word[0])
        answer = False
        save_wrong_answers(lesson_file, word[0])
    return answer

def start_guess(bigdict, questions, time, lesson_file):
  correct_answ = 0
  for word in bigdict:
    try:
      if question(word, questions, time, lesson_file):
        correct_answ += 1
      play_sound(word)
    except QuitException:
      return 0
    print
    print 'Press a button to continue'
    getch()

  os.system('clear')
  print_title('Result:')
  print
  percentage = int(100.0 * float(correct_answ) / float(len(bigdict)))
  print 'Score: %s/%s (%s%%)' % (correct_answ, len(bigdict), percentage)
  getch()
  return percentage

def start_sub_stage_write(questions, exercises, lesson_file):
  stage_name = exercises[0]
  choices = [i[0] for i in exercises[1]]

  if stage_name == 'Write reverse':
    questions = [ [i[1],i[0]] for i in questions]

  index = 0
  while True:
    os.system('clear')
    print_title(stage_name)
    i = 0
    for choice in choices:
      text = '%-10.10s (%s sec)' % (choice, str(exercises[1][i][TIME_INDEX]))
      if i == index:
        print_selected(text)
      else:
        print text
      i = i + 1
    print_footer()
    (index, action, quit) = handle_input(index, len(choices))
    if action:

      if is_arabic(questions[0][1]):
        clear()
        raw_input('Change to arabic keyboard and press enter!')

      bigdict = []
      for i in range(0, exercises[1][index][ITERATION_INDEX]):
        iteration = list(questions)
        random.shuffle(iteration)
        bigdict += iteration

      percentage = start_write(bigdict, exercises[1][index][TIME_INDEX], index, "Training" in choices[index], lesson_file)
        # only set percentage if its the exam
      if index != len(choices) - 1:
        percentage = 0
      else:
        return percentage
    if quit:
      return 0

  return percentage

def start_write(bigdict, time, index, print_answer, lesson_file):
  correct_answ = 0
  for question in bigdict:
    clear()
    print_title('Write The Correct Answer')
    if is_arabic(question[1]):
      print 'Choose Arabic keyboard!!!'
      print 'LAYOUT:'
      print
      print 'q=ق  w=ش  e=ع  r=ر  t=ت  y=ط  u=و  i=ي  o=ه  p=ة  å=ث  å=ظ'
      print '   a=ا  s=س  d=د  f=ف  g=غ  h=ح  j=ج  k=ك  l=ل' 
      print '     z=ز  x=خ  c=ص  v=ذ  b=ب  n=ن  m=م'
      print
      print 'vocals: alt-a = a   alt-u = u   alt-i = i'
      print 'variants: shift-i = ـى (alif maqsura)    shift-o = ـة (t / h / ẗ)'
      print 'hamza (ء): shift-3 = أ  * = إ'
      print_devider()
    if print_answer:
      print 'Question %s = %s, write %s below: ' % (question[0], question[1], bcolors.GREEN + question[1] + bcolors.ENDC)
    else:
      print 'Question (write answer): ' + question[0]
    print bcolors.BLUE
    text = raw_input_timed('-> ', time)
    print bcolors.ENDC
    if text == 'q':
      return 0
    elif text.lower().replace(' ', '') == question[1].encode('utf-8').lower().replace(' ', ''):
      print_green('Correct answer!')
      correct_answ += 1
    else:
      print_red('Wrong! Should be: %s' % question[1])
      save_wrong_answers(lesson_file, question[1])

    play_sound(question)
    raw_input('Press enter to continue')
  clear()
  os.system('clear')
  print_title('Result:')
  percentage = int(100.0 * float(correct_answ) / float(len(bigdict)))
  print 'Score: %s/%s (%s%%)' % (correct_answ, len(bigdict), percentage)
  getch()
  if is_arabic(bigdict[0][1]):
    raw_input('Change to NON arabic keyboard and press enter!')
  return percentage

def start_sub_stage(questions, exercises, lesson_file):
  stage_name = exercises[0]
  choices = [i[0] for i in exercises[1]]

  if stage_name == 'Guess reverse':
    questions = [ [i[1],i[0]] for i in questions]

  index = 0
  while True:
    os.system('clear')
    print_title(stage_name)
    i = 0
    for choice in choices:
      text = '%-10.10s (%s sec)' % (choice, str(exercises[1][i][TIME_INDEX]))
      if i == index:
        print_selected(text)
      else:
        print text
      i = i + 1
    print_footer()
    (index, action, quit) = handle_input(index, len(choices))
    if action:
      bigdict = []
      for i in range(0, exercises[1][index][ITERATION_INDEX]):
        iteration = list(questions)
        random.shuffle(iteration)
        bigdict += iteration

      percentage = start_guess(bigdict, questions, exercises[1][index][TIME_INDEX], lesson_file)
        # only set percentage if its the exam
      if index != len(choices) - 1:
        percentage = 0
      else:
        return percentage
    if quit:
      return 0

  return percentage

def start_stage(stage_id, stage, dic, lesson_file, progress, exercises):
  choices = ['Overview'] + [name[0] for name in exercises]
  index = 0
  while True:
    os.system('clear')
    print_title("Stage: " + str(stage_id))
    i = 0
    for choice in choices:
      prog = ''
      locked = ''
      if i != 0 and not progress[str(stage_id)].has_key(str(i)):
        progress[str(stage_id)][str(i)] = 0
      if i != 0:
        prog = '(%s)' % print_percentage(progress[str(stage_id)][str(i)])
      if i >= 2:
        locked = "Locked" if progress[str(stage_id)][str(i-1)] < 85 else ""
      text = '%-15.15s %s %s' % (choice, prog, locked)
      if i == index:
        print_selected(text)
      else:
        print text
      i = i+1
    print_footer()

    (index, action, quit) = handle_input(index, len(choices))
    if action:
      questions = dic[stage[0]:stage[1]]
      if (index == 0):
        clear()
        print_title(choices[index])
        for quest in questions:
          print '%-8s %-10s' % ((quest[0] + ':'), quest[1])
        print
        print 'Press any key to continue'
        getch()
      else:
        if index < 2 or progress[str(stage_id)][str(index-1)] > 85:
          if 'Write' in choices[index]:
            percentage = start_sub_stage_write(questions, exercises[index-1], lesson_file)
          else:
            percentage = start_sub_stage(questions, exercises[index-1], lesson_file)

          if not progress[str(stage_id)].has_key(str(index)):
            progress[str(stage_id)][str(index)] = 0
          if progress[str(stage_id)][str(index)] < percentage:
            progress[str(stage_id)][str(index)] = percentage

          with open(savefile(lesson_file), 'w+') as fd:
            fd.write(json.dumps(progress))
            fd.flush()
        else:
          print 'LOCKED'
          getch()

    if quit:
      break

def is_unlocked(exercises, progress, i):
    nr_exercises = len([name[0] for name in exercises])
    return i == 0 or (progress.has_key(str(i-1)) and progress[str(i-1)][str(nr_exercises)] >= 85)

def print_percentage(prog):
    if prog > 85:
      prog = bcolors.GREEN + str(prog) + '%' + bcolors.ENDC
    elif prog > 50:
      prog = bcolors.BLUE + str(prog) + '%' + bcolors.ENDC
    else:
      prog = bcolors.RED + str(prog) + '%' + bcolors.ENDC
    return prog

def load_wrong_answers(lesson_file):

  # load wrong answers
  if isfile(wrongfile(lesson_file)):
    with open(wrongfile(lesson_file), 'r') as fd:
        wrong_answers = json.loads(fd.read())
  else:
    wrong_answers = {}
    with open(wrongfile(lesson_file), 'w+') as fd:
      fd.write(json.dumps(wrong_answers))
      fd.flush()
  return wrong_answers

def save_wrong_answers(lesson_file, word):
  with open(wrongfile(lesson_file), 'r') as fd:
    wrong_answers = json.loads(fd.read())
  with open(wrongfile(lesson_file), 'w+') as fd:
    if not word in wrong_answers:
      wrong_answers[word] = 1
    else:
      wrong_answers[word] += 1
    fd.write(json.dumps(wrong_answers))
    fd.flush()

def enter_lesson(lesson_file):
  # load progress
  if isfile(savefile(lesson_file)):
    with open(savefile(lesson_file), 'r') as fd:
        progress = json.loads(fd.read())
  else:
    progress = {}
  clear()
  index = 0
  with open(lesson_file) as fdlesson:
    lesson = json.loads(fdlesson.read())
  dic = lesson["words"]
  exercises = lesson["exercises"]
  LESSON_SIZE = lesson["size"]
  multiplier = 5
  stages = []
  extra_uneven = 1 if (len(dic) % LESSON_SIZE) != 0 else 0
  for i in range(0, (len(dic) / LESSON_SIZE) + extra_uneven):
    start = i * LESSON_SIZE
    end = min((i + 1) * LESSON_SIZE, len(dic))
    stages.append((start, end))
    back = i 
    while back > 0:
      stages.append((back*LESSON_SIZE - LESSON_SIZE, end))
      back -= 1
    
  if test:
      start_stage(0, stages[0], dic, lesson_file, exercises)
  while True:
    wrong_answers = load_wrong_answers(lesson_file)
    os.system('clear')
    print_title('Lesson: %s' % lesson_file)
    total = 0
    for i in range(min(len(stages), 15)):
      prog = 0
      try:
        stage_total = reduce(lambda x, y: x+y, progress[str(i)].values())
        prog = int(float(stage_total) / (100 * len(progress[str(i)].values())) * 100)
        total += prog
      except:
        pass
      prog = print_percentage(prog)

      if is_unlocked(exercises, progress, i):
        if is_arabic(dic[stages[i][0]][1]):
          text = "%-5s %s %-10.20s " % (str(i) + ':', prog, (dic[stages[i][1] - 1][1] + ' <- ' + dic[stages[i][0] ][1]))
        else:
          text = "%-10.10s %-10.20s  %s" % (str(i) + ':', (dic[stages[i][0]][1] + ' -> ' + dic[stages[i][1] - 1][1]), prog)
      else:
        text = "%-10.10s %s" % (str(i) + ':', get_red('Locked'))
      if i == index:
        print_selected(text)
      else:
        print text
    print
    print '%-5s Display wrong answers' % 'e:'
    print_footer('Total: %s points' % total)
    (index, action, quit) = handle_input(index, len(stages))
    if action == 'e':
      sorted_wrong = sorted(wrong_answers.items(), key=operator.itemgetter(1))
      clear()
      print 'Top words you have problems with'
      for wrong in sorted_wrong:
        print u"{}: {}".format(wrong[1], wrong[0])
      getch()
    elif action:
      if is_unlocked(exercises, progress, index):
        if not progress.has_key(str(index)):
          progress[str(index)] = {}

        stage_progress = start_stage(index, stages[index], dic, lesson_file, progress, exercises)
      else:
        print_red('STAGE IS LOCKED')
        getch()
    if quit:
      break

def main():
  # create save path
  if not os.path.exists(savepath()):
    os.mkdir(savepath())
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
