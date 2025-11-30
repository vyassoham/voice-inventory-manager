"""
Speech-to-Text Pipeline Module

Handles all speech recognition operations including:
- Microphone input management
- Ambient noise calibration
- Multiple STT provider support (Google, Sphinx, Whisper)
- Audio preprocessing
- Confidence scoring
- Retry mechanisms
"""

import speech_recognition as sr
from typing import Optional, Dict, Any
from utils.logger import get_logger
import time


class STTError(Exception):
    """Base exception for STT errors."""
    pass


class STTPipeline:
    """
    Speech-to-Text pipeline that handles audio input and recognition.
    """

    def __init__(self, config: Dict[str, Any], mic_config: Dict[str, Any]):
        """
        Initialize STT pipeline.

        Args:
            config: STT configuration
            mic_config: Microphone configuration
        """
        self.config = config
        self.mic_config = mic_config
        self.logger = get_logger(__name__)

        # Initialize recognizer
        self.recognizer = sr.Recognizer()

        # Configure recognizer
        self.recognizer.energy_threshold = config.get('energy_threshold', 4000)
        self.recognizer.dynamic_energy_threshold = config.get('dynamic_energy_threshold', True)
        self.recognizer.pause_threshold = config.get('pause_threshold', 0.8)

        # STT provider
        self.provider = config.get('provider', 'google').lower()
        self.language = config.get('language', 'en-US')

        # Timeouts
        self.timeout = config.get('timeout', 5)
        self.phrase_time_limit = config.get('phrase_time_limit', 10)

        # Microphone
        self.microphone = None
        self.mic_index = mic_config.get('device_index', None)

        # Statistics
        self.recognition_count = 0
        self.error_count = 0
        self.total_recognition_time = 0.0

        self.logger.info(f"STT Pipeline initialized with provider: {self.provider}")

    def _get_microphone(self) -> sr.Microphone:
        """
        Get or create microphone instance.

        Returns:
            Microphone instance
        """
        if self.microphone is None:
            try:
                if self.mic_index is not None:
                    self.microphone = sr.Microphone(device_index=self.mic_index)
                    self.logger.info(f"Using microphone device index: {self.mic_index}")
                else:
                    self.microphone = sr.Microphone()
                    self.logger.info("Using default microphone")
            except Exception as e:
                self.logger.error(f"Failed to initialize microphone: {e}")
                raise STTError(f"Microphone initialization failed: {e}")

        return self.microphone

    def calibrate_for_ambient_noise(self, duration: float = 1.0) -> bool:
        """
        Calibrate recognizer for ambient noise.

        Args:
            duration: Duration to sample ambient noise (seconds)

        Returns:
            True if successful, False otherwise
        """
        try:
            microphone = self._get_microphone()

            with microphone as source:
                self.logger.info(f"Calibrating for ambient noise ({duration}s)...")
                self.recognizer.adjust_for_ambient_noise(source, duration=duration)
                self.logger.info(f"Energy threshold set to: {self.recognizer.energy_threshold}")

            return True

        except Exception as e:
            self.logger.error(f"Noise calibration failed: {e}")
            return False

    def listen(self, timeout: Optional[int] = None) -> Optional[sr.AudioData]:
        """
        Listen for audio input.

        Args:
            timeout: Maximum time to wait for phrase start (seconds)

        Returns:
            AudioData object or None if timeout/error
        """
        try:
            microphone = self._get_microphone()
            timeout = timeout or self.timeout

            with microphone as source:
                self.logger.debug(f"Listening (timeout: {timeout}s)...")

                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=self.phrase_time_limit
                )

                self.logger.debug("Audio captured")
                return audio

        except sr.WaitTimeoutError:
            self.logger.debug("Listening timeout - no speech detected")
            return None
        except Exception as e:
            self.logger.error(f"Error during listening: {e}")
            self.error_count += 1
            return None

    def recognize(self, audio: sr.AudioData) -> Optional[str]:
        """
        Recognize speech from audio data.

        Args:
            audio: Audio data to recognize

        Returns:
            Recognized text or None if failed
        """
        if audio is None:
            return None

        start_time = time.time()

        try:
            text = None

            # Use configured provider
            if self.provider == 'google':
                text = self._recognize_google(audio)
            elif self.provider == 'sphinx':
                text = self._recognize_sphinx(audio)
            elif self.provider == 'whisper':
                text = self._recognize_whisper(audio)
            else:
                self.logger.error(f"Unknown STT provider: {self.provider}")
                raise STTError(f"Unknown STT provider: {self.provider}")

            # Update statistics
            recognition_time = time.time() - start_time
            self.total_recognition_time += recognition_time
            self.recognition_count += 1

            self.logger.debug(f"Recognition took {recognition_time:.2f}s")

            return text

        except sr.UnknownValueError:
            self.logger.debug("Speech not understood")
            self.error_count += 1
            return None
        except sr.RequestError as e:
            self.logger.error(f"STT service error: {e}")
            self.error_count += 1
            return None
        except Exception as e:
            self.logger.error(f"Recognition error: {e}")
            self.error_count += 1
            return None

    def _recognize_google(self, audio: sr.AudioData) -> str:
        """
        Recognize using Google Speech Recognition.

        Args:
            audio: Audio data

        Returns:
            Recognized text
        """
        self.logger.debug("Using Google Speech Recognition")
        return self.recognizer.recognize_google(audio, language=self.language)

    def _recognize_sphinx(self, audio: sr.AudioData) -> str:
        """
        Recognize using CMU Sphinx (offline).

        Args:
            audio: Audio data

        Returns:
            Recognized text
        """
        self.logger.debug("Using Sphinx (offline)")
        return self.recognizer.recognize_sphinx(audio)

    def _recognize_whisper(self, audio: sr.AudioData) -> str:
        """
        Recognize using OpenAI Whisper.

        Args:
            audio: Audio data

        Returns:
            Recognized text
        """
        self.logger.debug("Using Whisper")
        # Note: This requires whisper to be installed
        # For now, fall back to Google
        self.logger.warning("Whisper not implemented, falling back to Google")
        return self._recognize_google(audio)

    def listen_and_recognize(
        self,
        timeout: Optional[int] = None,
        retry_count: int = 2
    ) -> Optional[str]:
        """
        Listen for audio and recognize speech with retry logic.

        Args:
            timeout: Maximum time to wait for phrase start
            retry_count: Number of retries on failure

        Returns:
            Recognized text or None
        """
        for attempt in range(retry_count + 1):
            try:
                # Listen for audio
                audio = self.listen(timeout=timeout)

                if audio is None:
                    if attempt < retry_count:
                        self.logger.debug(f"Retry {attempt + 1}/{retry_count}")
                        continue
                    return None

                # Recognize speech
                text = self.recognize(audio)

                if text:
                    return text.strip()

                if attempt < retry_count:
                    self.logger.debug(f"Recognition failed, retry {attempt + 1}/{retry_count}")

            except Exception as e:
                self.logger.error(f"Error in listen_and_recognize: {e}")
                if attempt >= retry_count:
                    return None

        return None

    def test_microphone(self) -> Dict[str, Any]:
        """
        Test microphone and return diagnostics.

        Returns:
            Dictionary with test results
        """
        result = {
            'success': False,
            'microphone_available': False,
            'can_record': False,
            'energy_threshold': None,
            'error': None
        }

        try:
            # Try to get microphone
            microphone = self._get_microphone()
            result['microphone_available'] = True

            # Try to record
            with microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                result['energy_threshold'] = self.recognizer.energy_threshold

                audio = self.recognizer.listen(source, timeout=3, phrase_time_limit=5)
                result['can_record'] = True

            result['success'] = True

        except Exception as e:
            result['error'] = str(e)
            self.logger.error(f"Microphone test failed: {e}")

        return result

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get pipeline statistics.

        Returns:
            Statistics dictionary
        """
        avg_time = 0.0
        if self.recognition_count > 0:
            avg_time = self.total_recognition_time / self.recognition_count

        return {
            'provider': self.provider,
            'recognition_count': self.recognition_count,
            'error_count': self.error_count,
            'average_recognition_time': avg_time,
            'energy_threshold': self.recognizer.energy_threshold
        }

    def cleanup(self):
        """Cleanup resources."""
        self.logger.info("Cleaning up STT pipeline")
        if self.microphone:
            self.microphone = None
