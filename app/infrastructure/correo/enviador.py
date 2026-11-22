import logging
import os
import smtplib
from email.message import EmailMessage

logger = logging.getLogger(__name__)


class EnviadorCorreo:
    def __init__(
        self,
        smtp_host: str | None = None,
        smtp_port: int | None = None,
        mail_from: str | None = None,
    ):
        self.smtp_host = smtp_host or os.getenv("SMTP_HOST", "localhost")
        self.smtp_port = smtp_port or int(os.getenv("SMTP_PORT", "1025"))
        self.mail_from = mail_from or os.getenv("MAIL_FROM", "no-reply@centrogamer.cl")

    def enviar_recuperacion(self, destinatario: str, token: str) -> None:
        base_url = os.getenv("FRONTEND_RESET_URL", "http://localhost:8000/restablecer")
        enlace = f"{base_url}?token={token}"

        mensaje = EmailMessage()
        mensaje["Subject"] = "Recuperación de contraseña - Centro Gamer"
        mensaje["From"] = self.mail_from
        mensaje["To"] = destinatario
        mensaje.set_content(
            "Recibimos una solicitud para restablecer tu contraseña.\n\n"
            f"Usa este enlace o token dentro de los próximos 15 minutos:\n{enlace}\n\n"
            f"Token: {token}\n\n"
            "Si no solicitaste este cambio, ignora este correo."
        )

        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10) as servidor:
                servidor.send_message(mensaje)
        except Exception:
            logger.exception("Error al enviar correo de recuperación vía SMTP")