/**
 * @file Lógica de la interfaz de AI Chat Assistant.
 *
 * Toda la comunicación con el backend se realiza con `fetch`. Las respuestas
 * del modelo se insertan en el DOM mediante `textContent` o creando nodos,
 * nunca con `innerHTML`, para evitar inyección de HTML.
 */

"use strict";

/**
 * Muestra un mensaje de error dentro de un contenedor.
 *
 * @param {HTMLElement} container - Elemento donde se mostrará el mensaje.
 * @param {string} message - Texto del error.
 * @returns {void}
 */
function showError(container, message) {
    container.replaceChildren();
    const paragraph = document.createElement("p");
    paragraph.className = "error-message";
    paragraph.textContent = message;
    container.appendChild(paragraph);
}

/**
 * Sustituye el contenido de un contenedor por un párrafo de texto plano.
 *
 * @param {HTMLElement} container - Elemento que se actualizará.
 * @param {string} text - Texto a mostrar.
 * @returns {void}
 */
function setParagraph(container, text) {
    container.replaceChildren();
    const paragraph = document.createElement("p");
    paragraph.textContent = text;
    container.appendChild(paragraph);
}

/** Caja donde se acumula la conversación. */
const chatBox = document.getElementById("chat-box");
/** Campo de texto del mensaje. */
const inputField = document.getElementById("user-input");
/** Botón que envía el mensaje. */
const sendButton = document.getElementById("send-button");

/**
 * Añade un mensaje al historial del chat y hace scroll al final.
 *
 * @param {string} author - Autor del mensaje ("You" o "AI").
 * @param {string} message - Texto del mensaje.
 * @returns {void}
 */
function appendMessage(author, message) {
    const paragraph = document.createElement("p");
    const strong = document.createElement("strong");
    strong.textContent = `${author}:`;
    paragraph.appendChild(strong);
    paragraph.appendChild(document.createTextNode(` ${message}`));
    chatBox.appendChild(paragraph);
    chatBox.scrollTop = chatBox.scrollHeight;
}

/**
 * Envía el mensaje al backend y añade la respuesta al historial.
 *
 * @async
 * @function sendMessage
 * @param {Event} event - Evento de clic del botón.
 * @returns {Promise<void>} No devuelve valor; actualiza el DOM.
 */
async function sendMessage(event) {
    event.preventDefault();

    const userMessage = inputField.value;
    appendMessage("You", userMessage);
    inputField.value = "";

    try {
        const response = await fetch(`/chat?prompt=${encodeURIComponent(userMessage)}`, {
            method: "POST",
        });

        if (!response.ok) {
            appendMessage("AI", "Error: Failed to fetch response.");
            return;
        }

        const data = await response.json();
        appendMessage("AI", data.response);
    } catch (error) {
        appendMessage("AI", "Error: Failed to fetch response.");
    }
}

document.addEventListener("DOMContentLoaded", () => {
    sendButton.addEventListener("click", sendMessage);
});
