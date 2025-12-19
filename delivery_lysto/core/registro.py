"""
--------------------------------------------
Configura logs a stdout y a archivo (rotating file handler) usando
la ruta definida en `Configuracion.LOG_FILE`.
"""
import logging
import logging.handlers
import os
import sys
from typing import Optional
from ..configuracion import Configuracion


class CappedFileHandler(logging.handlers.RotatingFileHandler):
    """Handler que mantiene solo las últimas N líneas en disco."""

    def __init__(self, *args, max_lines: int = 200, **kwargs):
        self.max_lines = max_lines
        super().__init__(*args, **kwargs)

    def emit(self, record: logging.LogRecord) -> None:
        super().emit(record)
        if not self.max_lines or self.max_lines <= 0:
            return
        try:
            with open(self.baseFilename, "r+", encoding=self.encoding or "utf-8") as f:
                lines = f.readlines()
                if len(lines) > self.max_lines:
                    f.seek(0)
                    f.writelines(lines[-self.max_lines:])
                    f.truncate()
        except Exception:
            # No interrumpir el flujo de logging ante errores de truncado
            pass


def configurar_logging(nivel: str = "INFO", logfile: Optional[str] = None) -> None:
    """Configura el sistema de logging de la aplicación.

    - nivel: Nivel de logs (DEBUG, INFO, WARNING, ERROR)
    - logfile: ruta opcional para archivo de logs; si no se pasa usa Configuracion.LOG_FILE
    """
    nivel_upper = nivel.upper() if isinstance(nivel, str) else "INFO"
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, nivel_upper, logging.INFO))

    formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s - %(message)s")

    # Stream handler (stdout)
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(formatter)
    sh.setLevel(getattr(logging, nivel_upper, logging.INFO))

    # File handler con rotación
    logfile = logfile or getattr(Configuracion, "LOG_FILE", None)
    handlers = [sh]
    if logfile:
        # Asegurar que el directorio exista
        logdir = os.path.dirname(logfile) or "."
        try:
            os.makedirs(logdir, exist_ok=True)
        except Exception:
            # Si falla crear el directorio, seguimos solo con stdout
            logfile = None

    if logfile:
        try:
            max_lines_cfg = int(getattr(Configuracion, "LOG_MAX_LINES", 200))
        except Exception:
            max_lines_cfg = 200

        fh = CappedFileHandler(
            logfile,
            maxBytes=0,  # sin rotación por tamaño; truncamos por líneas
            backupCount=0,
            encoding="utf-8",
            max_lines=max_lines_cfg,
        )
        fh.setFormatter(formatter)
        fh.setLevel(getattr(logging, nivel_upper, logging.INFO))
        handlers.append(fh)

    # Limpiar handlers anteriores y añadir los nuevos
    for h in list(root_logger.handlers):
        root_logger.removeHandler(h)

    for h in handlers:
        root_logger.addHandler(h)
