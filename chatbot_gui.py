import google.generativeai as genai  # pip install google-generativeai
import tkinter as tk  # pip install tk
from tkinter import scrolledtext
import threading  # pip install thread
import queue  # Import the queue module
from apikey import api_data

GENAI_API_KEY = api_data
genai.configure(api_key=GENAI_API_KEY)


def generate_response(query, conversation_history=None):
    """Generate a response for the given query using Gemini, with conversation history."""
    try:
        # Construct the prompt, including previous interactions
        prompt = ""
        if conversation_history:
            for turn in conversation_history:
                prompt += f"{turn}\n"  # Add previous turns to the prompt
        prompt += f"You: {query}\nJarvis:"  # Add the current query

        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                max_output_tokens=200, temperature=0.2
            ),  # Increased tokens, reduced temp
        )
        print("\n")
        return response.text
    except Exception as e:
        return f"Sorry, I encountered an error: {e}"


# Global variable to control the conversation loop
stop_conversation = False
# Use a queue to safely pass user input from the GUI thread to the conversation thread
query_queue = queue.Queue()


def handle_conversation():
    """Continuously get user input from the queue and respond."""
    global stop_conversation
    conversation_history = (
        []
    )  # Initialize conversation history *inside* handle_conversation
    while not stop_conversation:
        try:
            query = query_queue.get(
                timeout=0.1
            )  # Non-blocking get with timeout
            # print(f"Query from queue: {query}")  # For debugging
        except queue.Empty:
            continue  # No input yet, continue the loop

        conversation_area.insert(
            tk.END, f"You: {query}\n", "user"
        )  # Display user query
        conversation_area.tag_config("user", foreground="yellow")
        conversation_history.append(
            f"You: {query}"
        )  # Store user query in history

        if "bye" in query or "goodbye" in query:
            response = "Goodbye! Have a great day!"
            conversation_area.insert(
                tk.END, f"Jarvis: {response}\n", "jarvis"
            )  # Display bot response
            conversation_area.tag_config("jarvis", foreground="green")
            conversation_history.append(
                f"Jarvis: {response}"
            )  # Store bot response
            break

        # Generate and respond to the user's query
        response = generate_response(
            query, conversation_history
        )  # Pass history
        conversation_area.insert(
            tk.END, f"Jarvis: {response}\n", "jarvis"
        )  # Display bot response
        conversation_area.tag_config("jarvis", foreground="green")
        conversation_history.append(
            f"Jarvis: {response}"
        )  # Store bot response
        conversation_area.see(tk.END)



def start_conversation():
    """Start the conversation"""
    global stop_conversation
    stop_conversation = False
    conversation_thread = threading.Thread(target=handle_conversation)
    conversation_thread.daemon = True
    conversation_thread.start()
    initial_message = "Hi, I am Jarvis. How can I help you?"
    conversation_area.insert(tk.END, f"{initial_message}\n\n", "jarvis_init")
    conversation_area.tag_config("jarvis_init", foreground="green")
    conversation_area.see(tk.END)




def end_conversation():
    """Set the stop_conversation flag to True to end the loop."""
    global stop_conversation
    stop_conversation = True
    goodbye_message = "Conversation ended manually. Goodbye!"
    conversation_area.insert(tk.END, f"Jarvis: {goodbye_message}\n", "jarvis")
    conversation_area.tag_config("jarvis", foreground="green")
    root.quit()  # Close the application


def send_query():
    """Send the user's query to the conversation thread via the queue."""
    query = conversation_input.get()
    conversation_input.delete(0, tk.END)  # Clear the input
    query_queue.put(query)  # Put the query in the queue



# Set up the GUI
root = tk.Tk()
root.title("J-A-R-V-I-S")
root.config(bg="black")

conversation_area = scrolledtext.ScrolledText(
    root, wrap=tk.WORD, width=50, height=20, font=("Arial", 12), bg="black", fg="white"
)
conversation_area.pack(padx=10, pady=10)

# Input box for the user to type their query
conversation_input = tk.Entry(
    root, width=50, font=("Arial", 12), bg="black", fg="yellow", insertbackground="yellow"
)
conversation_input.pack(padx=10, pady=5)

# Send button
send_button = tk.Button(
    root, text="Send", font=("Arial", 12), command=send_query, bg="gray"
)
send_button.pack(pady=5)


# Start button
start_button = tk.Button(
    root, text="Start Conversation", font=("Arial", 12), command=start_conversation, bg="gray"
)
start_button.pack(pady=5)

# End button
end_button = tk.Button(
    root, text="End Conversation", font=("Arial", 12), command=end_conversation, bg="gray"
)
end_button.pack(pady=5)

# Bind Enter key to send_query function
conversation_input.bind("<Return>", lambda event: send_query())

root.mainloop()
