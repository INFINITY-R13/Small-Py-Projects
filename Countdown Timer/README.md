# ⏰ Countdown Timer / Alarm

A simple **Countdown Timer / Alarm** built with **Python and Tkinter**. The application provides a graphical interface where users can enter a countdown duration, start or pause the timer, reset it, and receive an alarm when the countdown reaches zero.

## ✨ Features

* ⏱️ Set a timer using minutes and seconds
* ▶️ Start the countdown
* ⏸️ Pause the countdown
* 🔄 Reset the timer
* ▶️ Resume a paused timer
* ⏰ Alarm notification when the timer reaches `00:00`
* 🔊 System beep/alarm sound
* 🚫 Input validation for invalid time values
* 🖥️ Simple and user-friendly Tkinter interface
* 📦 No external Python packages required

## 🛠️ Technologies Used

* **Python 3**
* **Tkinter** - GUI framework
* **winsound** - Windows alarm sound
* **Tkinter `after()`** - Non-blocking countdown mechanism

## 📁 Project Structure

```text
Countdown Timer/
│
├── main.py
└── README.md
```

## 🚀 Getting Started

### 1. Clone or download the project

Download the project to your computer.

### 2. Open the project directory

```bash
cd "Countdown Timer"
```

### 3. Run the application

```bash
python main.py
```

Depending on your Python installation, you may need:

```bash
python3 main.py
```

## 🖥️ How to Use

### Step 1: Enter the time

Enter the desired duration in the **Minutes** and **Seconds** fields.

For example:

```text
Minutes: 1
Seconds: 30
```

This sets a timer for **1 minute and 30 seconds**.

### Step 2: Start the timer

Click the **▶ Start** button.

The timer will begin counting down.

### Step 3: Pause the timer

Click **⏸ Pause** to temporarily stop the countdown.

Click **▶ Start** again to resume it.

### Step 4: Reset the timer

Click **🔄 Reset** to stop the timer and clear the current countdown.

### Step 5: Wait for the alarm

When the countdown reaches:

```text
00:00
```

the application will play an alarm sound and display a notification indicating that the timer has finished.

## 🧠 How It Works

The application uses Tkinter's `after()` method to update the countdown every second.

Instead of using:

```python
time.sleep(1)
```

the program uses:

```python
root.after(1000, update_timer)
```

This is important because `time.sleep()` would block Tkinter's event loop and make the GUI appear frozen.

The remaining time is converted into minutes and seconds using:

```python
minutes, seconds = divmod(remaining_seconds, 60)
```

The display is then updated every second.

## 🔊 Alarm Sound

On **Windows**, the application uses Python's built-in `winsound` module:

```python
import winsound

winsound.Beep(1000, 500)
```

On **macOS and Linux**, it falls back to Tkinter's system bell:

```python
root.bell()
```

The exact sound depends on the operating system and system settings.

## ✅ Input Validation

The application checks that:

* Minutes are not negative
* Seconds are not negative
* Seconds are less than `60`
* The total timer duration is greater than `0`
* The user enters valid numeric values

For example, this is invalid:

```text
Minutes: 2
Seconds: 75
```

because seconds must be between `0` and `59`.

## 📌 Example

If the user enters:

```text
Minutes: 0
Seconds: 10
```

the timer displays:

```text
00:10
00:09
00:08
00:07
...
00:02
00:01
00:00
```

After reaching zero, the alarm plays and a notification appears:

```text
⏰ Time's up!
```

## 📚 Concepts Practiced

This project is useful for practicing:

* Python functions
* Classes and objects
* Tkinter GUI development
* Event-driven programming
* Button callbacks
* Input validation
* Countdown logic
* `after()` scheduling
* Exception handling
* Basic cross-platform sound handling

## 🔮 Future Improvements

Possible improvements include:

* 🎵 Custom alarm sounds
* 🔁 Repeat/loop alarm
* ⏯️ Start, pause, and resume controls
* 🎨 Custom themes and colors
* 🌙 Dark mode
* 📊 Progress bar
* 🔔 Multiple alarm sound options
* ⌨️ Keyboard shortcuts
* 💾 Save frequently used timer durations
* 🕒 Add a clock alongside the countdown

## 📄 License

This project is open-source and available for personal and educational use.
