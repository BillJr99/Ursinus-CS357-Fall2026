---
layout: default-standard
permalink: /Tutorials/Shell
title: 'CS357: Foundations of Artificial Intelligence - The Shell, in Full'
info:
  coursenum: CS357
  purpose: "To take you from your first terminal prompt to fluent command-line work, so that you can read and supervise every shell command an agent proposes to run on your behalf."
tags:
- shell
- tooling
- setup
---

# CS357: Foundations of Artificial Intelligence - The Shell, in Full

## Purpose

To take you from your first terminal prompt to fluent command-line work, so that you can read and supervise every shell command an agent proposes to run on your behalf.

## About This Tutorial

Every agentic CLI tool you will meet this semester (Claude Code, Codex, Gemini CLI, opencode, pi, and the rest) lives in the **terminal**, and when those agents act, they act by running shell commands on your behalf.  You cannot supervise what you cannot read.  This tutorial takes you from your very first prompt to fluent command-line work, assuming nothing.  We move today from **what a shell is $\rightarrow$ moving around $\rightarrow$ working with files $\rightarrow$ pipes and redirection $\rightarrow$ environment and PATH $\rightarrow$ processes $\rightarrow$ the terminal inside VS Code**.

## Key Concepts

These terms turn up all through this tutorial.  Read them once before you start; they are the vocabulary you need to decode everything else.

| Term | Plain-English Definition | Where You'll Meet It |
|---|---|---|
| **Shell** | A program that reads a line of text you type, runs the named command, and prints the result back to you; think of it as a conversation between you and the operating system. | `bash` or `zsh` running inside your terminal window |
| **Terminal** | The window or application that hosts the shell and displays its text; the shell is the engine, the terminal is the dashboard. | Terminal.app on macOS; Windows Terminal on Windows; any terminal emulator on Linux |
| **Working Directory** | The folder the shell considers your current location; every relative file path is measured from here. | Shown in the prompt as `~/projects`; confirmed by running `pwd` |
| **PATH** | An ordered list of directories the shell searches, left to right, whenever you type a command name; if a program is not in any of those directories, the shell says "command not found." | `echo $PATH` reveals something like `/usr/local/bin:/usr/bin:/bin` |
| **Pipe** | The `|` character that connects two commands by routing the first command's output directly into the second command's input, without saving anything to a file in between. | `grep "ERROR" agent.log \| wc -l` counts error lines |
| **Environment Variable** | A named value stored in the shell's memory and passed automatically to every program the shell launches, the standard way to supply configuration and secrets without hardcoding them. | `ANTHROPIC_API_KEY=sk-litellm-local` tells Claude Code which key to use |

---

### Before You Start

**What you need:** A terminal. macOS and Linux have one; on Windows use WSL. Nothing else installed.

**What you will have at the end:** the handful of shell moves every later lab assumes, practiced rather than read.

Please go through the sections in order, and run each code block as you hit it.  Reading past them will cost you later.

---

# Part I: Orientation

In this Part, you will learn what a shell is, how to navigate the filesystem, and how to read and decode a compound shell command before running it.  By the end, you will be able to look at any agent-proposed command and explain what it does, the first requirement for safe agent supervision.

## 1.  What a Shell Actually Is

Think of the terminal as your agent's native language, like learning to read blueprints instead of just looking at buildings.  A finished building (a GUI application) hides all the structural decisions; blueprints (shell commands) expose every beam, pipe, and wire.  When you can read blueprints, you can verify that what your agent proposed is safe before any concrete is poured.  This section teaches you to read the blueprints.

A shell is a program that reads a line of text, runs the command it names, and shows you the result.  The window the shell lives in is the **terminal** (on macOS, Terminal.app or iTerm2; on Windows, Windows Terminal running PowerShell or, better for this course, WSL with Ubuntu; on Linux, any terminal emulator).  The shell we assume is **bash** or its close cousin **zsh** (the macOS default); their everyday commands are identical.

**Anatomy of the prompt.**  When you open a terminal you see something like `bill@laptop:~/projects$`.  Read it as a sentence: user `bill`, machine `laptop`, current directory `~/projects` (the `~` means your home directory), and `$` meaning "I am ready."  Everything you type until Enter is one command: a program name, then **arguments**, separated by spaces.  Options (also called flags) usually begin with `-` or `--`.

**Why agents make this matter.**  When Claude Code proposes `rm -rf build/` and asks for permission, the permission gate is only as good as your ability to read that line.  The shell is the contract language between you and your agent; this tutorial teaches you to read contracts before signing them.

## 2.  Moving Around

Before you can read or modify files, you need to know where you are and how to move around.  The following six commands cover almost all navigation you will ever do in the shell.

Three commands carry most navigation.  The following snippet shows each command alongside a comment explaining what it does; run each one in your terminal and observe the output before moving on.  Pay special attention to how `cd ..` and `cd -` complement each other: one moves you up the tree, the other undoes the last move.

```bash
pwd                  # print working directory: where am I right now?
ls                   # list all files and folders here
ls -la               # list everything including hidden files, with full details (size, owner, date)
cd projects          # change directory INTO the folder named "projects"
cd ..                # go UP one level to the parent folder
cd ~                 # jump directly to your home directory, no matter where you are
cd -                 # jump back to wherever you just were (like a browser Back button)
```

The filesystem is a tree.  Paths beginning with `/` are **absolute** (measured from the root of the entire tree); paths without a leading `/` are **relative** (measured from where you stand right now). `.` means "the current directory"; `..` means "the parent directory."  Press **Tab** to autocomplete names (the single biggest speed upgrade available), and the up arrow to recall previous commands. `history` shows everything you have typed, which is also how you will audit what an agent typed.

---

## Read Before You Run

Think of the terminal as your agent's native language, like learning to read blueprints instead of just looking at buildings.  This model asks you to study one compound command the way an architect reads a blueprint (word by word, symbol by symbol) before allowing any construction to begin.  Your agent will propose lines like this one routinely; the skill of parsing them before approving them is the core competency of this course.

An agent proposes the sequence below.  Decode every line before you run any of it:

```bash
cd ~/projects/demo && ls -la && cat config.json | head -20
```

Breaking it down piece by piece:

- `cd ~/projects/demo`: change into the folder `demo` inside your home directory's `projects` subfolder
- `&&`: only run the next command if the previous one succeeded (exit code 0)
- `ls -la`: list all files in the new directory, with details and hidden files shown
- `cat config.json`: print the entire contents of `config.json` to the screen
- `| head -20`: pass that output through a pipe and show only the first 20 lines (`head` takes `-N` where N is the number of lines)

### Questions to Work Through

1.  Translate the entire line into one plain English sentence.  What does `&&` appear to do, and what would you predict happens to `ls -la` and `cat config.json | head -20` if `cd ~/projects/demo` fails because the directory does not exist?

   *Hint:* Run `cd /this-does-not-exist && echo "I ran!"` in your terminal and observe whether `echo` executes.  The exit code of `cd` controls whether `&&` continues.

2.  The agent could have proposed three separate commands on three separate lines.  Name one concrete advantage and one concrete risk of chaining all three with `&&` from a supervision standpoint; think about what you see in the approval dialog versus what you can catch line by line.

   *Hint:* Consider how many approval prompts you receive for one chained line versus three separate lines, and whether a fast-scrolling terminal makes the middle command easier or harder to spot.

3.  Find the part of the line you could not fully explain after reading the breakdown above, and resolve it by running `man head` or `head --help` in your terminal.  Write down the flag or concept you looked up and what you learned.  The manual is the ground truth, and reading it is a professional skill, not an admission of weakness.

   *Hint:* Type `man head` and press `q` to quit when done.  If `man` is unavailable (some Windows setups), try `head --help` instead.

---

# Part II: Files, Pipes, and Plumbing

In this Part, you will learn the commands for creating, reading, moving, and deleting files, and the critical pipe (`|`) and redirection operators that connect commands into powerful one-liners.  You will also encounter the two shell commands that deserve the most caution: `rm` and `rm -rf`.

## 3.  Working with Files

The table below covers the ten commands you will use most often when working with files in the shell.  Pay special attention to `rm` and `rm -r`; unlike most commands, they are permanent and irreversible.

| Command | What It Does | Example Command |
|---|---|---|
| `mkdir lab1` | Creates a new empty directory named `lab1` in the current location | `mkdir lab1` creates `./lab1/` |
| `touch notes.md` | Creates an empty file if it does not exist; updates its modification timestamp if it does | `touch notes.md`, safe to run on an existing file |
| `cp notes.md backup.md` | Copies `notes.md` to a new file named `backup.md`; both files exist afterward | `cp notes.md backup.md` |
| `mv backup.md old/` | Moves `backup.md` into the `old/` directory; also used to rename: `mv old.txt new.txt` | `mv backup.md old/` |
| `cat notes.md` | Prints the entire contents of `notes.md` to the screen at once | `cat notes.md` |
| `less big.log` | Pages through a large file one screen at a time; press `q` to quit, `/keyword` to search forward | `less big.log` |
| `head -5 data.csv` | Prints only the first 5 lines of `data.csv`; change `5` to any number | `head -20 data.csv` shows the first 20 lines |
| `tail -f agent.log` | Follows a file as it grows, printing new lines as they arrive; essential for watching live logs; press `Ctrl+C` to stop | `tail -f agent.log` |
| `rm scratch.txt` | Permanently deletes `scratch.txt`; there is NO undo and NO trash can | `rm scratch.txt` |
| `rm -r scratch_dir/` | Recursively deletes `scratch_dir/` and everything inside it; treat this like a chainsaw | `rm -r scratch_dir/` |

**The two commands that deserve fear.** `rm` is permanent, and `rm -rf` (force + recursive, often combined) is the chainsaw of the shell.  The `-f` flag suppresses all confirmation prompts.  Our course governance principle applies to you exactly as it applies to your agents: destructive actions get a pause, a re-read, and ideally a backup first. `tail -f` is the opposite: a gift, and the standard way to watch a container or agent log scroll by in real time.

## 4.  Pipes and Redirection: The Unix Superpower

Pipes and redirection let you compose simple commands into powerful one-liners without ever saving intermediate results to a file.  This is the same composition idea that underlies agent pipelines: small, focused tools chained together to produce complex results.

**A pipe `|` sends one command's output into the next command's input**, composing small tools into pipelines.  The three examples below each build a chain from left to right; read each one as a sentence ("search for X, then count the results") and predict the output before running it in your terminal.

```bash
grep "ERROR" agent.log | wc -l

# grep searches agent.log for lines containing "ERROR" and passes them to wc

# wc -l counts the number of lines received; result is the total error count

ls -la | sort -k5 -n | tail -3

# ls -la lists files with details; sort -k5 -n sorts by the 5th column (file size) numerically

# tail -3 keeps only the last 3 lines; result is the three largest files

cat results.csv | grep "fail" | head -10

# cat prints results.csv; grep keeps only lines containing "fail"

# head -10 keeps only the first 10 of those; result is the first ten failures
```

Redirection sends output to files instead of the screen.  Use `>` to overwrite, `>>` to append, and `2>` to capture error messages separately.  Read the comments in the block below carefully before running any of these; the difference between `>` and `>>` is one character but the consequences are very different, and the `2>` line is the one you will reach for every time a script crashes silently.

```bash
python run_eval.py > results.txt

# Runs run_eval.py and saves ALL standard output to results.txt

# WARNING: this OVERWRITES results.txt entirely if it already exists

python run_eval.py >> results.txt

# Same, but APPENDS to results.txt instead of overwriting; safe for accumulating runs

python run_eval.py > out.txt 2> err.txt

# Saves normal output to out.txt AND saves error messages to err.txt separately

# The "2>" targets file descriptor 2, which is the error stream
```

The four workhorses worth memorizing by name are `grep` (search text for a pattern), `wc` (count lines, words, or characters), `sort` (sort lines), and `find` (search for files by name or type: `find . -name "*.json"` finds all JSON files under the current directory).  Everything else can be looked up as needed.

A teammate runs `python eval.py > results.txt` twice in a row with different settings, intending to compare the two runs.  What happened to the first run's results?

[( )] They appear above the second run's results in the file; this is how `>>` (append) works, but `>` does not accumulate output; it overwrites from the first byte of the new run
[(X)] They were overwritten and are gone, because > truncates the file before writing; >> would have appended
[( )] They were automatically backed up to `results.txt.bak` by the shell; the shell provides no automatic backup mechanism; silent overwrite is the default behavior and there is no undo
[( )] The second run failed silently because the file already existed; `>` does not check whether the destination file exists; it opens, truncates, and writes unconditionally

---

> **Common Misconception:** Many beginners read `>` as "send output to" and assume it accumulates, the way a chat window adds new messages.  It does not.  The `>` operator truncates (erases) the destination file to zero bytes before writing the first byte of new output.  If you run `python eval.py > results.txt` a second time, the first run's data is gone before the second run even finishes.  Always use `>>` when you intend to keep previous results, and consider naming output files by run number or timestamp (e.g., `results_run1.txt`, `results_run2.txt`) when you need to compare them later.

---

### Questions to Work Through

4.  Write a single pipeline that searches `agent.log` for lines containing the word `WARN`, counts them, and also saves just those `WARN` lines to a file called `warnings.txt`, all in one command.  (Hint: `tee` is a command that sends output to both a file and to standard output simultaneously.  Try `grep "WARN" agent.log | tee warnings.txt | wc -l`.)

   *Hint:* The exact command syntax is `grep "WARN" agent.log | tee warnings.txt | wc -l`.  Run it and confirm that `warnings.txt` exists and contains the expected lines.

5.  Explain in one sentence why `python run_eval.py > out.txt 2> err.txt` is more useful for debugging an agent script than `python run_eval.py > out.txt` alone.

   *Hint:* Ask yourself: when a Python script crashes, where does the traceback go, to standard output or to the error stream?  Run `python -c "raise ValueError('test')" > out.txt` and check whether anything appears in `out.txt`.

6.  A teammate proposes `rm -rf logs/ 2> /dev/null` to silently delete the logs directory and suppress any error messages.  Before approving this in an agent permission dialog, what two things would you want to verify?

   *Hint:* Consider (a) whether `logs/` might contain files that cannot be recreated, and (b) what `/dev/null` does to error messages that would otherwise warn you the deletion failed.

---

*You now know how to navigate and compose file operations.  Before launching any agent tool, you need to understand environment variables (the mechanism that supplies configuration and API keys to those tools) and PATH, which controls whether the shell can find them at all.*

## 5.  Environment Variables and PATH

**Environment variables** (the shell's persistent key-value settings, named values the shell stores in memory and automatically passes to every program it launches, so programs can read configuration without hardcoded paths or secrets) are named values the shell passes to every program it starts; think of them as the shell's global settings.  They are how this course's tools receive configuration and credentials without you having to hardcode those values into your code.  The following block shows the four most important environment variable operations for this course; note that `export` is what makes a variable visible to child processes like Claude Code; without it, the variable exists only in your current shell session and the tool cannot see it.

```bash
echo $HOME

# Prints the value of the HOME variable, your home directory path

export ANTHROPIC_BASE_URL=http://localhost:4000

# Creates (or overwrites) the variable ANTHROPIC_BASE_URL and marks it for export

# "export" means child processes (like Claude Code) will inherit this value

export ANTHROPIC_API_KEY=sk-litellm-local

# Sets the API key that Claude Code reads on startup

env | grep ANTHROPIC

# env lists ALL current environment variables; grep filters to only ANTHROPIC ones

# Use this to confirm your variables are set correctly before launching a tool
```

Variables set with `export` last only until the terminal closes; to make them permanent, append the export lines to `~/.bashrc` (or `~/.zshrc` on macOS) and run `source ~/.bashrc` to reload the file in the current session.  **Never paste a real secret into a file that might be committed to git**; we return to secret handling in the publishing module.

PATH is the list of directories the shell searches to find commands.  When you type `claude` and the shell says `command not found`, the diagnosis is almost always one of two things: the tool is not installed, or it is installed somewhere not on your PATH. `which python3` shows where a command resolves; `echo $PATH` shows the search list.  This single concept explains most installation frustration you will ever feel.

### Questions to Work Through

7.  Run `echo $PATH` in your terminal and count how many directories are listed (they are separated by `:`).  Now run `which python3`.  Which directory in your PATH contains `python3`?

   *Hint:* The exact command is `echo $PATH | tr ':' '\n'`; the `tr ':' '\n'` part replaces each `:` separator with a newline so you can read one directory per line.  Then compare each directory to the output of `which python3`.

8.  Explain why two teammates might type `python3 --version` and see different version numbers, even though they are on the same course server.

   *Hint:* The PATH is searched left to right and stops at the first match.  If one teammate has `/home/alice/.local/bin` earlier in their PATH than `/usr/bin`, and that directory contains a different `python3`, that version wins.  Run `echo $PATH` on both machines and compare the order.

*With environment variables and PATH understood, you can launch agent tools and know they will find their configuration.  The final piece is managing the programs themselves: how to run them in the background, check on them, and stop them when needed.*

## 6.  Processes

Every running program is a **process** (a running instance of a program, assigned a unique process ID number, PID, by the operating system so it can be tracked and stopped independently of other programs).  The controls you need.  The sequence below covers the full lifecycle: starting a process in the foreground, interrupting it, launching one in the background, finding it by name, and stopping it gracefully or forcibly, in that order.

```bash
some_long_command

# Runs in the foreground; your prompt disappears and waits until the command finishes

Ctrl+C

# Sends an interrupt signal to the foreground process; politely asks it to stop immediately

some_server &

# The & at the end runs the command in the background; your prompt returns immediately

# The shell prints the background job's PID (process ID number) so you can track it

ps aux | grep ollama

# ps aux lists every running process on the system with details

# grep ollama filters to only lines mentioning "ollama"; shows PID, CPU, memory

kill 12345

# Sends a polite termination signal (SIGTERM) to process number 12345

# Replace 12345 with the actual PID from ps aux

kill -9 12345

# Sends an immediate, uncatchable kill signal (SIGKILL); use only if kill 12345 fails

# The process cannot clean up after itself, so use this as a last resort
```

When a port is "already in use" (a constant companion in the Docker module), `lsof -i :3000` names the process holding port 3000, and now you know how to evict it.

### Questions to Work Through

9.  A teammate's agent started a local model server in the background with `ollama serve &`.  Ten minutes later they close the terminal; is the server still running?  How would you check, and how would you stop it?

   *Hint:* Closing a terminal does not automatically kill background processes.  Run `ps aux | grep ollama` in a new terminal to check.  If it is running, copy the PID from the second column and run `kill <PID>`.

10.  Explain in one sentence why `kill -9` is described as a "last resort" rather than the default way to stop a process.

    *Hint:* Think about what a server process might need to do before it exits: closing database connections, flushing write buffers, saving state. A SIGKILL prevents all of that. Try looking up "SIGTERM vs SIGKILL" if you want the full picture.

---

*You can now navigate, manage files, compose pipelines, set environment variables, and control processes.  Part III brings all of this together in the tool you will use every day: VS Code's integrated terminal, where your agent runs in one pane while you review its changes in another.*

# Part III: The Terminal in VS Code, and Practice

In this Part, you will bring everything together in the tool you will use every day this semester: VS Code's integrated terminal.  Understanding how the editor and terminal share a workspace is what lets you supervise agent edits in one pane while reading their file changes in another, the exact workflow the rest of the course depends on.

## 7.  VS Code Is a Terminal with an Editor Attached

VS Code's integrated terminal puts your agent's command output and its file edits side by side in one window, so you never need to switch between the terminal and the editor to see what an agent proposal actually changes.

Open VS Code's integrated terminal with **Ctrl+`** (backtick). It is a full shell, opened in your project's folder automatically, which is exactly where agent CLIs want to be launched: `claude`, `codex`, `gemini`, `opencode`, and `pi` all start in the current directory and treat it as their workspace. The split is natural: the agent runs in the terminal pane while you read its edits in the editor pane above, with VS Code's diff coloring showing every change the agent makes the moment it makes it. The agent CLI module builds on this layout; today, just confirm you can open the panel, run `pwd`, and see your project path.

### Questions to Work Through

11.  Open the VS Code integrated terminal and run `pwd`.  Does the path it prints match the folder you have open in the VS Code Explorer sidebar?  If not, what command would bring the terminal to the same location?

    *Hint:* The terminal opens in VS Code's "workspace root", the top-level folder you opened with `File > Open Folder`. If they differ, `cd` to the correct path, or close and reopen the terminal after opening the right folder.

---

## 8.  Exercises

1.  **Treasure hunt.**

   *What to do:* In your terminal, create a directory tree `lab/{data,logs,out}` (three subdirectories inside `lab/` all at once), create three `.md` files inside `data/`, then write a single pipeline that counts how many `.md` files exist anywhere under `lab/`.  Record the pipeline and the count.

   *Starter hint:* Begin with `mkdir -p lab/{data,logs,out}` (the `-p` flag creates parent directories as needed and does not error if they already exist).  Then `touch lab/data/a.md lab/data/b.md lab/data/c.md`.  For the count pipeline, start from `find lab/ -name "*.md" | wc -l`.

   *You have succeeded when:* `find lab/ -name "*.md" | wc -l` prints `3` and you can explain each piece of the pipeline to a teammate.

2.  **Log triage.**

   *What to do:* Download the provided `sample-agent.log` from the course site.  Using only `grep`, `wc`, `head`, `tail`, and pipes: (a) count the total number of ERROR lines, (b) show the last five WARN lines, and (c) save all ERROR lines to a file called `errors.txt`.  Use three commands or fewer.

   *Starter hint:* For (a): `grep "ERROR" sample-agent.log | wc -l`.  For (b): `grep "WARN" sample-agent.log | tail -5`.  For (c): `grep "ERROR" sample-agent.log > errors.txt`.  If you want to do (a) and (c) in one command, try `grep "ERROR" sample-agent.log | tee errors.txt | wc -l`.

   *You have succeeded when:* `errors.txt` exists and contains only ERROR lines, the WARN count you report matches what a teammate independently counted, and you used no more than three commands total.

3.  **PATH forensics.**

   *What to do:* Run `echo $PATH | tr ':' '\n'` to list every directory in your PATH one per line.  Then run `which python3` to find where `python3` lives.  Write one sentence explaining why two teammates on different machines might type `python3 --version` and see different version numbers.

   *Starter hint:* The key command is `echo $PATH | tr ':' '\n'` to list directories clearly, then `which python3` to see which one wins.  If you want to see every `python3` on your system (not just the first), try `type -a python3`.

   *You have succeeded when:* You can point to the specific directory in your PATH output that contains `python3`, and your one-sentence explanation mentions that PATH is searched left to right and stops at the first match.

4.  **Permission rehearsal.**

   *What to do:* Write one shell line that looks innocent on a quick glance but is actually destructive or has a surprising side effect.  Take turns reading each line aloud as a team and giving a verdict: "approve" or "deny," with one sentence of reasoning.  This is the exact skill the agent permission gate requires of you every time an agent proposes a command.

   *Starter hint:* Examples of deceptive-looking lines include: `cat file.txt > important.txt` (silently overwrites `important.txt`), `find . -name "*.log" -delete` (deletes files without showing them first), or `mv * /tmp/` (moves everything in the current directory to `/tmp/`).  Try to write one that would fool a teammate reading quickly.

   *You have succeeded when:* Every teammate can articulate the exact danger in each line and would not need to look it up, meaning the pattern is memorized, not just recognized.

5.  **Dotfile setup.**

   *What to do:* Add one quality-of-life improvement to your `~/.bashrc` (Linux) or `~/.zshrc` (macOS).  Good options: an alias like `alias ll='ls -la'` so `ll` gives you a detailed listing, or an alias like `alias gs='git status'`, or a PATH addition for a tool you installed that keeps saying "command not found."  Run `source ~/.bashrc` (or `~/.zshrc`) to load the change, verify it works in the current terminal, then open a brand-new terminal and verify it persists.

   *Starter hint:* Open the file with `nano ~/.bashrc`, scroll to the bottom, add your alias on a new line, press `Ctrl+X` then `Y` then `Enter` to save.  Then run `source ~/.bashrc` and type your new alias to confirm it works.

   *You have succeeded when:* Your alias or PATH change works in a freshly opened terminal (not just the one where you ran `source`), proving the file was saved correctly and not just applied to the current session.

---

## Reflection Prompt

In your notebook, respond at three levels:

**Personal level:** The shell gives no warnings, no confirmations, and no undo, yet you probably use apps every day that ask "are you sure?" for every deletion.  How does that contrast make you feel about working in the terminal?  Did today's session shift that feeling at all, and if so, what changed?

**Technical level:** The permission-gated contract our agent tools offer (the agent proposes, you approve or deny) is a deliberate layer added on top of the raw shell.  Based on today's session, name two specific shell behaviors (redirection, `rm -rf`, background processes, PATH resolution, or something else you encountered) that you would want an agent's permission gate to highlight or warn about, and explain why those two in particular.

**Societal level:** Professionals who can read and write shell commands have historically had significant power over systems and data that non-technical users cannot see or audit.  As agent tools extend shell access to people who never learned the command line, what responsibilities do the builders of those permission gates carry?  Who should decide what counts as "dangerous enough to require approval"?

> *Hint:* Consider two analogies: (1) a car's power steering makes driving easier without exposing the hydraulics, but driving instructors still teach the underlying mechanics.  (2) A bank's mobile app lets non-experts move money without understanding ACH transfers, but regulators set limits on what the app can do without extra authentication.  Which analogy fits agent shell tools better, and what does the better-fit analogy imply about where the "dangerous enough" threshold should be set and who should set it?

---

## Coming Up Next

Now that you can navigate the filesystem, manage files, compose pipelines, and interpret environment variables, you have the vocabulary to read everything an agent proposes before approving it.  The next module puts this vocabulary to immediate use: you will launch Claude Code (and at least one other agent CLI) in VS Code's integrated terminal, walk through the permission dialog for a real multi-step coding task, and compare how different agents phrase the same shell operations.  The habits you built today (pause, read the full line, check for `&&` chains and redirections, verify PATH) are exactly the habits the next module will stress-test.

---

## 9.  Further Reading

- MIT, "The Missing Semester of Your CS Education" (online): the shell lectures, a superb deeper pass.
- William Shotts.  *The Linux Command Line* (free PDF online): the patient book-length treatment.
- `man bash`, sections on pipelines and redirection, once you are brave.
