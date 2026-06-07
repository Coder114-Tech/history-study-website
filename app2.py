import streamlit as st
import os
import json
import random
from PIL import Image

# Page config
st.set_page_config(page_title="City of Victoria Study Tool", layout="centered")

IMAGE_DIR = ""
DATA_FILE = "buildings_data.json"

# Load saved user data
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        learning_data = json.load(f)
else:
    learning_data = []

st.title("🏛️ City of Victoria Study Tool")

# Track flipped image paths globally in session state
if 'flipped_images' not in st.session_state:
    st.session_state.flipped_images = set()

# Helper function to load and display image (handles temporary 180 flip)
def display_building_image(image_path):
    if os.path.exists(image_path):
        img = Image.open(image_path)
        if image_path in st.session_state.flipped_images:
            img = img.rotate(180)
        st.image(img, use_container_width=True)
        
        # Quick flip button right under the image
        if st.button("🔄 Flip Image 180°", key=f"flip_{image_path}"):
            if image_path in st.session_state.flipped_images:
                st.session_state.flipped_images.remove(image_path)
            else:
                st.session_state.flipped_images.add(image_path)
            st.rerun()
    else:
        st.warning(f"Missing photo: {image_path}")

# Check if data exists
if not learning_data:
    st.error("⚠️ No data found! Make sure 'buildings_data.json' and your 'extracted_images' folder are uploaded to GitHub.")
else:
    # Navigation Sidebar
    mode = st.sidebar.radio("Choose Mode", ["📚 Flashcards Mode", "🎯 Training Mode"])

    # ---------------------------------------------------------
    # FLASHCARDS MODE
    # ---------------------------------------------------------
    if mode == "📚 Flashcards Mode":
        st.subheader("Flashcards (Swipe & Reveal)")
        
        if 'flash_idx' not in st.session_state:
            st.session_state.flash_idx = 0
        if 'revealed' not in st.session_state:
            st.session_state.revealed = False

        current = learning_data[st.session_state.flash_idx]
        
        # Display Progress
        st.write(f"Card {st.session_state.flash_idx + 1} of {len(learning_data)}")

        # Display Image with flip functionality
        display_building_image(current["image_path"])

        # Reveal logic
        if st.session_state.revealed:
            st.success(f"### Name: {current['name']}")
        else:
            if st.button("👁️ Click to Reveal Name"):
                st.session_state.revealed = True
                st.rerun()

        # Navigation buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("◄ Previous"):
                st.session_state.flash_idx = (st.session_state.flash_idx - 1) % len(learning_data)
                st.session_state.revealed = False
                st.rerun()
        with col2:
            if st.button("Next ►"):
                st.session_state.flash_idx = (st.session_state.flash_idx + 1) % len(learning_data)
                st.session_state.revealed = False
                st.rerun()

    # ---------------------------------------------------------
    # TRAINING MODE
    # ---------------------------------------------------------
    elif mode == "🎯 Training Mode":
        st.subheader("Infinite Mastery Training")

        # Initialize training queue
        if 'queue' not in st.session_state or not st.session_state.queue:
            st.session_state.queue = list(learning_data)
            random.shuffle(st.session_state.queue)
            st.session_state.mastered = 0
            st.session_state.feedback = None

        if len(st.session_state.queue) == 0:
            st.balloons()
            st.success("🎉 Mastery Complete! You correctly named all buildings!")
            if st.button("🔄 Restart Training"):
                del st.session_state.queue
                st.rerun()
        else:
            current_train = st.session_state.queue[0]
            
            # Progress bar
            progress = st.session_state.mastered / len(learning_data)
            st.progress(progress)
            st.write(f"Mastered: {st.session_state.mastered} / {len(learning_data)} | Items left in queue: {len(st.session_state.queue)}")

            # Display Image with flip functionality
            display_building_image(current_train["image_path"])

            # Input form
            with st.form(key="guess_form", clear_on_submit=True):
                guess = st.text_input("Name this building:").strip().lower()
                submit = st.form_submit_button("Submit Answer")

                if submit and guess:
                    if guess in [a.lower() for a in current_train["aliases"]]:
                        st.session_state.feedback = ("correct", f"✅ Correct! Moving to the next building.")
                    else:
                        st.session_state.feedback = ("incorrect", f"❌ Incorrect! The answer was: **{current_train['name']}**. Pushing this to the back of the queue.")

            # Show text feedback and next button
            if st.session_state.feedback:
                status, msg = st.session_state.feedback
                if status == "correct":
                    st.success(msg)
                else:
                    st.error(msg)
                
                if st.button("Continue ➔"):
                    if status == "correct":
                        st.session_state.queue.pop(0)
                        st.session_state.mastered += 1
                    else:
                        item = st.session_state.queue.pop(0)
                        st.session_state.queue.append(item)
                    st.session_state.feedback = None
                    st.rerun()
