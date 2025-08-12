# 🍉 Fruit Ninja - Air Slice (Gesture Controlled)

A Python-based **gesture-controlled Fruit Ninja game** built using **PyGame**, **OpenCV**, and **MediaPipe**.  
Instead of using a mouse or touchscreen, you slice fruits **in the air** using your hands detected via webcam!  

🎯 **No physical controller, just pure hand-tracking magic!**  

🎮 **Game Features**
✅ Gesture-controlled slicing using MediaPipe hand tracking\n
✅ Smooth fruit physics with gravity\n
✅ Combo scoring system for quick multiple hits\n
✅ Lives & Game Over screen\n
✅ Fun sound effects and visuals\n

---

## 📹 Demo Video

---

## 🛠 Tech Stack
- **Python 3.8+**
- **PyGame** – Game rendering & logic  
- **OpenCV** – Camera input & frame processing  
- **MediaPipe** – Hand detection & tracking  
- **Math & Random** – Physics & random fruit spawn  
- **Collections (deque)** – Smooth slicing trails

---

## 📂 Project Structure
| File | Description |
|------|-------------|
| `main.py` | Main game script – contains all logic for fruit spawning, slicing, scoring, and life tracking. |
| `assets` | Game images (fruits, bombs, background) and sound effects. |
| `README.md` | Project documentation. |
| `requirements.txt` | Python dependencies for easy installation. |

---

## 🚀 How to Run
1. **Clone the repo**
   ```bash
   git clone https://github.com/navyajain7105/Fruit_Ninja_Air_Slice_Using_PyGame_OpenCV_MediaPipe.git
   cd Fruit_Ninja_Air_Slice_Using_PyGame_OpenCV_MediaPipe

2. **Install dependencies**
    ```bash
    pip install -r requirements.txt

3. **Run the game**
   ```bash
   python main.py

4. **Play!**
    -Stand in front of your webcam\n
    -Move your hand to slice fruits\n
    -Avoid slicing bombs!\n
