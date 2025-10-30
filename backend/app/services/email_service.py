"""
Email Service
Email gönderme işlemleri
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from fastapi import HTTPException, status
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """Email sending service"""

    @staticmethod
    def _send_email(
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """
        Email gönder (internal method)

        Args:
            to_email: Alıcı email
            subject: Email konusu
            html_content: HTML içerik
            text_content: Plain text içerik (opsiyonel)

        Returns:
            Success
        """
        try:
            # SMTP credentials kontrolü
            if not settings.SMTP_USER or not settings.SMTP_PASS:
                logger.warning("SMTP credentials not configured, skipping email send")
                return False
            # Email mesajı oluştur
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{settings.FROM_NAME} <{settings.FROM_EMAIL}>"
            msg['To'] = to_email
            msg['Subject'] = subject

            # Plain text ekle (varsa)
            if text_content:
                part1 = MIMEText(text_content, 'plain')
                msg.attach(part1)

            # HTML ekle
            part2 = MIMEText(html_content, 'html')
            msg.attach(part2)

            # SMTP sunucusuna bağlan ve gönder
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASS)
                server.send_message(msg)

            logger.info(f"Email sent successfully to {to_email}")
            return True

        except Exception as e:
            logger.error(f"Email sending error: {str(e)}")
            return False

    @staticmethod
    async def send_verification_email(
        email: str,
        full_name: str,
        token: str
    ) -> bool:
        """
        Email verification email'i gönder

        Args:
            email: Alıcı email
            full_name: Kullanıcı adı
            token: Verification token

        Returns:
            Success
        """
        try:
            # Verification URL
            verification_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"

            # Email konusu
            subject = "MarkaMind - Email Adresinizi Doğrulayın"

            # HTML içerik
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        line-height: 1.6;
                        color: #333;
                        background-color: #f4f4f4;
                        margin: 0;
                        padding: 0;
                    }}
                    .container {{
                        max-width: 600px;
                        margin: 20px auto;
                        background-color: #ffffff;
                        border-radius: 8px;
                        overflow: hidden;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    }}
                    .header {{
                        background-color: #6434F8;
                        color: #ffffff;
                        padding: 30px;
                        text-align: center;
                    }}
                    .content {{
                        padding: 30px;
                    }}
                    .button {{
                        display: inline-block;
                        padding: 12px 30px;
                        background-color: #6434F8;
                        color: #ffffff;
                        text-decoration: none;
                        border-radius: 5px;
                        margin: 20px 0;
                    }}
                    .footer {{
                        background-color: #f4f4f4;
                        padding: 20px;
                        text-align: center;
                        font-size: 12px;
                        color: #666;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>MarkaMind'e Hoş Geldiniz!</h1>
                    </div>
                    <div class="content">
                        <p>Merhaba {full_name},</p>
                        <p>MarkaMind'e kaydolduğunuz için teşekkür ederiz. Hesabınızı aktifleştirmek için lütfen email adresinizi doğrulayın.</p>
                        <p style="text-align: center;">
                            <a href="{verification_url}" class="button">Email Adresimi Doğrula</a>
                        </p>
                        <p>Eğer buton çalışmıyorsa, aşağıdaki linki tarayıcınıza kopyalayabilirsiniz:</p>
                        <p style="word-break: break-all; color: #666; font-size: 12px;">{verification_url}</p>
                        <p><strong>Not:</strong> Bu link {settings.EMAIL_VERIFICATION_EXPIRE_HOURS} saat geçerlidir.</p>
                        <p>Eğer bu hesabı siz oluşturmadıysanız, bu email'i görmezden gelebilirsiniz.</p>
                    </div>
                    <div class="footer">
                        <p>&copy; 2024 MarkaMind. Tüm hakları saklıdır.</p>
                    </div>
                </div>
            </body>
            </html>
            """

            # Plain text içerik
            text_content = f"""
            Merhaba {full_name},

            MarkaMind'e kaydolduğunuz için teşekkür ederiz. Hesabınızı aktifleştirmek için lütfen email adresinizi doğrulayın.

            Doğrulama linki: {verification_url}

            Bu link {settings.EMAIL_VERIFICATION_EXPIRE_HOURS} saat geçerlidir.

            Eğer bu hesabı siz oluşturmadıysanız, bu email'i görmezden gelebilirsiniz.

            © 2024 MarkaMind. Tüm hakları saklıdır.
            """

            # Email'i gönder
            success = EmailService._send_email(
                to_email=email,
                subject=subject,
                html_content=html_content,
                text_content=text_content
            )

            if not success:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Email gönderilemedi"
                )

            return True

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Verification email error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Email gönderme hatası: {str(e)}"
            )

    @staticmethod
    async def send_password_reset_email(
        email: str,
        full_name: str,
        token: str
    ) -> bool:
        """
        Password reset email'i gönder

        Args:
            email: Alıcı email
            full_name: Kullanıcı adı
            token: Reset token

        Returns:
            Success
        """
        try:
            # Reset URL
            reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"

            # Email konusu
            subject = "MarkaMind - Şifre Sıfırlama"

            # HTML içerik
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        line-height: 1.6;
                        color: #333;
                        background-color: #f4f4f4;
                        margin: 0;
                        padding: 0;
                    }}
                    .container {{
                        max-width: 600px;
                        margin: 20px auto;
                        background-color: #ffffff;
                        border-radius: 8px;
                        overflow: hidden;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    }}
                    .header {{
                        background-color: #6434F8;
                        color: #ffffff;
                        padding: 30px;
                        text-align: center;
                    }}
                    .content {{
                        padding: 30px;
                    }}
                    .button {{
                        display: inline-block;
                        padding: 12px 30px;
                        background-color: #6434F8;
                        color: #ffffff;
                        text-decoration: none;
                        border-radius: 5px;
                        margin: 20px 0;
                    }}
                    .warning {{
                        background-color: #fff3cd;
                        border-left: 4px solid #ffc107;
                        padding: 15px;
                        margin: 20px 0;
                    }}
                    .footer {{
                        background-color: #f4f4f4;
                        padding: 20px;
                        text-align: center;
                        font-size: 12px;
                        color: #666;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Şifre Sıfırlama</h1>
                    </div>
                    <div class="content">
                        <p>Merhaba {full_name},</p>
                        <p>Hesabınız için şifre sıfırlama talebinde bulundunuz. Yeni şifre oluşturmak için aşağıdaki butona tıklayın:</p>
                        <p style="text-align: center;">
                            <a href="{reset_url}" class="button">Şifremi Sıfırla</a>
                        </p>
                        <p>Eğer buton çalışmıyorsa, aşağıdaki linki tarayıcınıza kopyalayabilirsiniz:</p>
                        <p style="word-break: break-all; color: #666; font-size: 12px;">{reset_url}</p>
                        <div class="warning">
                            <p><strong>Güvenlik Uyarısı:</strong></p>
                            <ul>
                                <li>Bu link sadece {settings.PASSWORD_RESET_EXPIRE_HOURS} saat geçerlidir</li>
                                <li>Bu linki kimseyle paylaşmayın</li>
                                <li>Şifre sıfırlama talebinde bulunmadıysanız, bu email'i görmezden gelin</li>
                            </ul>
                        </div>
                    </div>
                    <div class="footer">
                        <p>&copy; 2024 MarkaMind. Tüm hakları saklıdır.</p>
                    </div>
                </div>
            </body>
            </html>
            """

            # Plain text içerik
            text_content = f"""
            Merhaba {full_name},

            Hesabınız için şifre sıfırlama talebinde bulundunuz.

            Şifre sıfırlama linki: {reset_url}

            GÜVENLİK UYARISI:
            - Bu link sadece {settings.PASSWORD_RESET_EXPIRE_HOURS} saat geçerlidir
            - Bu linki kimseyle paylaşmayın
            - Şifre sıfırlama talebinde bulunmadıysanız, bu email'i görmezden gelin

            © 2024 MarkaMind. Tüm hakları saklıdır.
            """

            # Email'i gönder
            success = EmailService._send_email(
                to_email=email,
                subject=subject,
                html_content=html_content,
                text_content=text_content
            )

            if not success:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Email gönderilemedi"
                )

            return True

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Password reset email error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Email gönderme hatası: {str(e)}"
            )

    @staticmethod
    async def send_welcome_email(email: str, full_name: str) -> bool:
        """
        Hoş geldin email'i gönder

        Args:
            email: Alıcı email
            full_name: Kullanıcı adı

        Returns:
            Success
        """
        try:
            subject = "MarkaMind'e Hoş Geldiniz!"

            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        line-height: 1.6;
                        color: #333;
                    }}
                    .container {{
                        max-width: 600px;
                        margin: 0 auto;
                        padding: 20px;
                    }}
                    .header {{
                        background-color: #6434F8;
                        color: white;
                        padding: 20px;
                        text-align: center;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Hoş Geldiniz!</h1>
                    </div>
                    <div class="content">
                        <p>Merhaba {full_name},</p>
                        <p>MarkaMind ailesine katıldığınız için teşekkür ederiz!</p>
                        <p>Artık tüm özelliklerimizden faydalanabilirsiniz.</p>
                    </div>
                </div>
            </body>
            </html>
            """

            return EmailService._send_email(
                to_email=email,
                subject=subject,
                html_content=html_content
            )

        except Exception as e:
            logger.error(f"Welcome email error: {str(e)}")
            return False
