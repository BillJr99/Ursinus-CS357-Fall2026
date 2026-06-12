# The Shell: Your Agent's Native Habitat
<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357/blob/gh-pages/_pages/Activities/liascript-shellbasics.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-shellbasics.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# The Shell: Your Agent's Native Habitat

Every agentic CLI tool you will meet this semester (Claude Code, Codex, Gemini CLI, opencode, pi, and the rest) lives in the **terminal**, and when those agents act, they act by running shell commands on your behalf. You cannot supervise what you cannot read. This tutorial takes you from your very first prompt to fluent command-line work, assuming nothing. The arc: **what a shell is $\rightarrow$ moving around $\rightarrow$ working with files $\rightarrow$ pipes and redirection $\rightarrow$ environment and PATH $\rightarrow$ processes $\rightarrow$ the terminal inside VS Code**.

---

## Directions and Group Roles

Throughout this course, we work in POGIL-style teams of three or four with rotating roles:

- **Manager**: keeps the team on task and watches the time.
- **Recorder**: writes the team's answers on the Class Activity Questions discussion board.
- **Presenter**: reports the team's findings to the class.
- **Reflector**: notes what helped or hindered the team, and shares one observation at the end.

Today is hands-on: every member opens a terminal and types every command personally (watching does not build muscle memory). The Recorder captures surprising outputs verbatim. After class, respond to the reflective prompt individually in your notebook.

---

# Part I: Orientation

## 1. What a Shell Actually Is

**A shell is a program that reads a line of text, runs the command it names, and shows you the result.** The window the shell lives in is the **terminal** (on macOS, Terminal.app or iTerm2; on Windows, Windows Terminal running PowerShell or, better for this course, WSL with Ubuntu; on Linux, any terminal emulator). The shell we assume is **bash** or its close cousin **zsh** (the macOS default); their everyday commands are identical.

**Anatomy of the prompt.** When you open a terminal you see something like `bill@laptop:~/projects$`. Read it as a sentence: user `bill`, machine `laptop`, current directory `~/projects` (the `~` means your home directory), and `$` meaning "I am ready." Everything you type until Enter is one command: a program name, then **arguments**, separated by spaces. Options (also called flags) usually begin with `-` or `--`.

**Why agents make this matter.** When Claude Code proposes `rm -rf build/` and asks for permission, the permission gate is only as good as your ability to read that line. The shell is the contract language between you and your agent; this tutorial teaches you to read contracts before signing them.

## 2. Moving Around

Three commands carry most navigation:

```bash
pwd                  # print working directory: where am I?
ls                   # list what is here
ls -la               # list everything, with details (and hidden dotfiles)
cd projects          # change directory into projects
cd ..                # go up one level
cd ~                 # jump home
cd -                 # jump back to wherever you just were
```

**The filesystem is a tree.** Paths beginning with `/` are **absolute** (from the root); paths without are **relative** (from where you stand). `.` means here; `..` means the parent. Press **Tab** to autocomplete names (the single biggest speed upgrade available), and the up arrow to recall previous commands. `history` shows everything you have typed, which is also how you will audit what an agent typed.

---

## Model 1: Read Before You Run

Your teammate's agent proposes this sequence. Decode it as a team before anyone executes anything:

```bash
cd ~/projects/demo && ls -la && cat config.json | head -20
```

### Critical Thinking Questions

1. Translate the line into one English sentence. What does `&&` appear to do, and what would you predict happens to the later commands if `cd` fails because the directory does not exist?
2. The agent could have proposed three separate commands. Name one advantage and one risk of chaining with `&&` from a supervision standpoint.
3. Find the part of the line you could not fully explain, and resolve it with `man head` or `head --help` (the manual is the ground truth, and reading it is a professional skill, not an admission of weakness).

---

# Part II: Files, Pipes, and Plumbing

## 3. Working with Files

```bash
mkdir lab1                   # make a directory
touch notes.md               # create an empty file (or update its timestamp)
cp notes.md backup.md        # copy
mv backup.md old/            # move (also how you rename)
cat notes.md                 # print a whole file
less big.log                 # page through a big file (q to quit, / to search)
head -5 data.csv             # first five lines
tail -f agent.log            # follow a growing log LIVE (Ctrl+C to stop)
rm scratch.txt               # delete a file (NO undo, NO trash can)
rm -r scratch_dir/           # delete a directory and contents (be afraid)
```

**The two commands that deserve fear.** `rm` is permanent, and `rm -rf` (force, recursive) is the chainsaw of the shell. Our course governance principle applies to you exactly as it applies to your agents: destructive actions get a pause, a re-read, and ideally a backup. `tail -f` is the opposite: a gift, and the standard way to watch a container or agent log scroll by in real time.

## 4. Pipes and Redirection: The Unix Superpower

**A pipe `|` sends one command's output into the next command's input**, composing small tools into pipelines, the same composition idea as our agent pipelines:

```bash
grep "ERROR" agent.log | wc -l            # count error lines
ls -la | sort -k5 -n | tail -3            # the three biggest files here
cat results.csv | grep "fail" | head -10  # first ten failures
```

**Redirection sends output to files instead of the screen**: `>` overwrites, `>>` appends, `2>` captures errors:

```bash
python run_eval.py > results.txt          # save output (OVERWRITES results.txt)
python run_eval.py >> results.txt         # append instead
python run_eval.py > out.txt 2> err.txt   # separate normal output from errors
```

`grep` (search text), `wc` (count), `sort`, and `find` (search for files: `find . -name "*.json"`) are the four workhorses worth memorizing; everything else can be looked up.

[[MC]]
A teammate runs `python eval.py > results.txt` twice in a row with different settings, intending to compare the two runs. What happened to the first run's results?
- ( ) They appear above the second run's results in the file
- (x) They were overwritten and are gone, because > truncates the file before writing; >> would have appended
- ( ) They were moved to results.txt.bak automatically
- ( ) Nothing; > only works once per file

---

## 5. Environment Variables and PATH

**Environment variables are named values the shell passes to every program it starts**, and they are how this course's tools receive configuration and credentials:

```bash
echo $HOME                                  # read a variable
export ANTHROPIC_BASE_URL=http://localhost:4000   # set one for this session
export ANTHROPIC_API_KEY=sk-litellm-local
env | grep ANTHROPIC                        # see what is set
```

Variables set with `export` last only until the terminal closes; to make them permanent, append the export lines to `~/.bashrc` (or `~/.zshrc` on macOS) and run `source ~/.bashrc`. **Never paste a real secret into a file that might be committed to git**; we return to secret handling in the publishing module.

**PATH is the list of directories the shell searches to find commands.** When you type `claude` and the shell says `command not found`, the diagnosis is almost always one of two things: the tool is not installed, or it is installed somewhere not on your PATH. `which python3` shows where a command resolves; `echo $PATH` shows the search list. This single concept explains most installation frustration you will ever feel.

## 6. Processes

Every running program is a **process**. The controls you need:

```bash
some_long_command            # runs in the foreground; the prompt waits
Ctrl+C                       # politely kill the foreground process
some_server &                # & runs it in the background
ps aux | grep ollama         # find a process and its PID
kill 12345                   # ask process 12345 to exit
kill -9 12345                # force it (last resort)
```

When a port is "already in use" (a constant companion in the Docker module), `lsof -i :3000` names the process holding port 3000, and now you know how to evict it.

---

# Part III: The Terminal in VS Code, and Practice

## 7. VS Code Is a Terminal with an Editor Attached

Open VS Code's integrated terminal with **Ctrl+`** (backtick). It is a full shell, opened in your project's folder automatically, which is exactly where agent CLIs want to be launched: `claude`, `codex`, `gemini`, `opencode`, and `pi` all start in the current directory and treat it as their workspace. The split is natural: the agent runs in the terminal pane while you read its edits in the editor pane above, with VS Code's diff coloring showing every change the agent makes the moment it makes it. The agent CLI module builds on this layout; today, just confirm you can open the panel, run `pwd`, and see your project path.

## 8. Exercises

1. *Treasure hunt.* In your terminal: create a directory tree `lab/{data,logs,out}` (three subdirectories), create three files in `data/`, then in one pipeline count how many `.md` files exist anywhere under `lab/`. Record the pipeline.
2. *Log triage.* Download the provided `sample-agent.log` from the course site. Using only `grep`, `wc`, `head`, `tail`, and pipes: count the ERROR lines, show the last five WARN lines, and save all ERROR lines to `errors.txt`. Three commands or fewer.
3. *PATH forensics.* Run `echo $PATH`, identify every directory in it, and find which one contains `python3` using `which`. One sentence: why might two teammates type the same command and get different versions?
4. *Permission rehearsal.* Each teammate writes one shell line that looks innocent but is destructive or surprising; the team takes turns reading them aloud and ruling approve or deny with a one-sentence reason. (This is the exact skill the agent permission gate requires.)
5. *Dotfile setup.* Add one quality-of-life line to your `~/.bashrc` or `~/.zshrc` (an alias like `alias ll='ls -la'`, or a PATH addition), `source` it, and verify it works in a new terminal.

---

## Reflection Prompt

In your notebook: the shell gives no warnings, no confirmations, and no undo, yet professionals trust it for the most critical work precisely because it does exactly what is typed. Compare this contract with the permission-gated contract our agent tools offer. Which would you rather supervise, and what does your answer imply about the interfaces you will build?

---

## 9. Further Reading

- MIT, "The Missing Semester of Your CS Education" (online): the shell lectures, a superb deeper pass.
- William Shotts. *The Linux Command Line* (free PDF online): the patient book-length treatment.
- `man bash`, sections on pipelines and redirection, once you are brave.
