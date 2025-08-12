# 🍉 Fruit Ninja - Air Slice (Gesture Controlled)

A Python-based **gesture-controlled Fruit Ninja game** built using **PyGame**, **OpenCV**, and **MediaPipe**.  
Instead of using a mouse or touchscreen, you slice fruits **in the air** using your hands detected via webcam!  

🎯 **No physical controller, just pure hand-tracking magic!**  

🎮 **Game Features**<br>
✅ Gesture-controlled slicing using MediaPipe hand tracking<br>
✅ Smooth fruit physics with gravity<br>
✅ Combo scoring system for quick multiple hits<br>
✅ Lives & Game Over screen<br>
✅ Fun sound effects and visuals<br>

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

4. **Play!**<br>
    -Stand in front of your webcam<br>
    -Move your hand to slice fruits<br>
    -Avoid slicing bombs!<br>
