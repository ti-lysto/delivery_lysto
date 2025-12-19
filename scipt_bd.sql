-- // Use DBML to define your database structure
-- // Docs: https://dbml.dbdiagram.io/docs

-- table tb_delivery_cliente{
--   id_cliente integer [primary key] 
--   tipo_documento char [primary key]
--   num_documento varchar (10) [primary key]
--   cod_cliente_zoom integer [not null]
--   login_zoom varchar [not null]
--   clave_zoom varchar [not null]
--   frase_secreta_zomm varchar [not null]  
--   telefono varchar (14)
--   mail varchar (20)
--   direccion varchar
--   cod_estatus_cliente integer
--   fecha_creacion datetime [not null]
--   fecha_actualizacion datetime
-- }

-- table tb_delivery_envio_cab{
--   id_envio_cab integer [primary key]
--   id_envio_track integer [primary key]
--   id_cliente integer [primary key]
--   id_empresa_Envio  int [not null]
--   referencia_interna VARCHAR [not null]
--   num_guia_envio varchar(50) [not null]
--   token_zoom varchar [not null]
--   remitente_nombre varchar(50) [not null]
--   remitente_direccion varchar (100) [not null]
--   destinatario_nombre varchar(50) [not null]
--   destinatario_codestado integer [not null]
--   destinatario_codmunicipio integer [not null]
--   destinatario_codparroquia integer [not null]
--   destinatario_ciudad integer [not null]
--   destinatario_direccion varchar (100) [not null]
--   retira_oficina bool [not null]
--   cod_oficinadestinatario integer [null]
--   destinatario_gps varchar(20) 
--   num_piezas integer [not null]
--   peso DECIMAL(10,3) [not null]
--   valor_mercancia DECIMAL(12,2) [not null] 
--   alto DECIMAL(12,2) [not null] 
--   ancho DECIMAL(12,2) [not null] 
--   largo DECIMAL(12,2) [not null] 
--   tipo_envio VARCHAR(50) 
--   seguro bool [not null]
--   tipo_servicio integer [not null]
--   estado_general VARCHAR(100) 
--   notas varchar  
--   payload_cab json 
--   fecha_envio datetime [not null]
--   fecha_entrega datetime
-- }

-- table tb_delivery_envio_track{
--   id_envio_track integer [primary key]
--   track_cod varchar (10) [not null]
--   track_descripcion varchar (100) [not null]
--   track_gps varchar(20)
--   track_fechora datetime [not null]
--   track_nota varchar
--   track_status varchar(50) [not null]
--   payload_track json
-- }

-- table tb_delivery_empresa_envio{
--   id_empresa_envio integer [primary key]
--   nombre_empresa_envio varchar(50) [not null]
--   numero_documento varchar(10) [not null]
--   descripcion varchar [null]
--   cod_estatus_empresa integer [not null]
--   fecha_creacion datetime [not null]
--   fecha_actualizacion datetime
-- }

-- table tb_estatus_general{
--   id_estatus_general integer [primary key]
--   cod_estatus integer [not null]
--   modulo_estatus varchar(100) [not null]
--   nombre_estatus varchar(50) [not null]
--   descripcion_estatus varchar(max) [not null]
--   fecha_creacion datetime [not null]
-- }



-- Ref: "tb_delivery_cliente"."id_cliente" < "tb_delivery_envio_cab"."id_cliente"

-- Ref: "tb_delivery_envio_cab"."id_envio_track" < "tb_delivery_envio_track"."id_envio_track"

-- Ref: "tb_delivery_empresa_envio"."id_empresa_envio" < "tb_delivery_envio_cab"."id_empresa_Envio"

-- Ref: "tb_estatus_general"."cod_estatus" < "tb_delivery_empresa_envio"."cod_estatus_empresa"

-- Ref: "tb_estatus_general"."cod_estatus" < "tb_delivery_cliente"."cod_estatus_cliente"




-- ┌─────────────────────────────────────────────────┐
-- │               SISTEMA PRINCIPAL                 │
-- ├─────────────────────────────────────────────────┤
-- │  tb_estatus_general    (ESTADOS CATÁLOGO)       │
-- │  tb_delivery_empresa_envio  (PROVEEDORES)       │
-- │  tb_delivery_cliente        (CLIENTES)          │
-- └─────────────────┬───────────────┬───────────────┘
--                   │               │
--     ┌─────────────▼─────┐ ┌───────▼───────────┐
--     │     MÓDULO ZOOM   │ │   MÓDULO ARMI     │
--     ├───────────────────┤ ├───────────────────┤
--     │ tb_delivery_envio │ │ tb_armi_pedidos   │
--     │      _cab         │ │ tb_armi_productos │
--     │ tb_delivery_envio │ │ tb_armi_tracking  │
--     │ _track_zoom       │ │ tb_armi_negocios  │
--     └───────────────────┘ │ tb_armi_sucursales│
--                           └───────────────────┘


CREATE TABLE `tb_delivery_cliente` (
  `id_cliente` int NOT NULL AUTO_INCREMENT,
  `tipo_cliente` varchar(20) NOT NULL DEFAULT 'CLIENTE_FINAL',
  `tipo_documento` char(1) NOT NULL,
  `num_documento` varchar(10) NOT NULL,
  `telefono` varchar(14) DEFAULT NULL,
  `mail` varchar(50) DEFAULT NULL,
  `direccion` varchar(200) DEFAULT NULL,
  `cod_cliente_zoom` int DEFAULT NULL,
  `cod_estatus_cliente` int NOT NULL DEFAULT '1',
  `fecha_creacion` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `fecha_actualizacion` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_cliente`),
  UNIQUE KEY `uk_documento` (`tipo_documento`,`num_documento`),
  KEY `idx_tipo_cliente` (`tipo_cliente`),
  KEY `idx_estatus` (`cod_estatus_cliente`),
  CONSTRAINT `tb_delivery_cliente_ibfk_1` FOREIGN KEY (`cod_estatus_cliente`) REFERENCES `tb_estatus_general` (`cod_estatus`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Tabla para registrar clientes que contratan servicios.\nUso: Quién paga/contrata el envío/pedido.\nIMPORTANTE: Puede ser TU empresa (INTEGRADOR) o un cliente final.\nEjemplo: id=1 INTEGRADOR, id=2 CLIENTE_FINAL\n';

CREATE TABLE `tb_delivery_empresa_envio` (
  `id_empresa_envio` int NOT NULL AUTO_INCREMENT,
  `nombre_empresa_envio` varchar(100) NOT NULL,
  `numero_documento` varchar(20) NOT NULL,
  `tipo_empresa` varchar(20) NOT NULL,
  `descripcion` varchar(255) DEFAULT NULL,
  `codigo_pais_default` varchar(3) DEFAULT 'COL',
  `cod_estatus_empresa` int NOT NULL DEFAULT '1',
  `fecha_creacion` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `fecha_actualizacion` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_empresa_envio`),
  KEY `idx_tipo_empresa` (`tipo_empresa`),
  KEY `idx_estatus` (`cod_estatus_empresa`),
  CONSTRAINT `tb_delivery_empresa_envio_ibfk_1` FOREIGN KEY (`cod_estatus_empresa`) REFERENCES `tb_estatus_general` (`cod_estatus`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Tabla para registrar empresas de envíos (ZOOM, ARMI, otras).\nUso: Saber qué proveedor usa cada envío/pedido.\nEjemplo: id=1 ZOOM, id=2 ARMI';

CREATE TABLE `tb_delivery_envio_cab_zoom` (
  `id_envio_cab` int NOT NULL AUTO_INCREMENT,
  `id_cliente` int NOT NULL,
  `id_empresa_envio` int NOT NULL,
  `cod_estatus_envio` int NOT NULL DEFAULT '1' COMMENT '1=CREADO, 2=RECIBIDO, etc.',
  `referencia_interna` varchar(50) NOT NULL,
  `id_guia_zoom` varchar(50) DEFAULT NULL,
  `referencia_zoom` varchar(50) DEFAULT NULL,
  `cod_cliente_zoom` int NOT NULL,
  `token_zoom` text,
  `certificado_zoom` text,
  `token_expiracion` datetime DEFAULT NULL,
  `remitente_nombre` varchar(100) NOT NULL,
  `contacto_remitente` varchar(100) DEFAULT NULL,
  `telefono_remitente` varchar(50) DEFAULT NULL,
  `remitente_direccion` text,
  `codciudad_remitente` int NOT NULL,
  `destinatario_nombre` varchar(100) NOT NULL,
  `contacto_destinatario` varchar(100) DEFAULT NULL,
  `telefono_destino` varchar(50) DEFAULT NULL,
  `destinatario_direccion` text,
  `codciudad_destinatario` int NOT NULL,
  `retira_oficina` tinyint(1) DEFAULT '0',
  `cod_oficina_destino` int DEFAULT NULL,
  `codservicio_zoom` int NOT NULL,
  `tipo_tarifa` int DEFAULT '1',
  `modalidad_tarifa` int DEFAULT '2',
  `modalidad_cod` int DEFAULT NULL,
  `num_piezas` int DEFAULT '1',
  `peso` decimal(10,3) NOT NULL,
  `alto` decimal(10,2) DEFAULT NULL,
  `ancho` decimal(10,2) DEFAULT NULL,
  `largo` decimal(10,2) DEFAULT NULL,
  `tipo_envio` char(1) DEFAULT 'M',
  `valor_mercancia` decimal(12,2) NOT NULL,
  `valor_declarado` decimal(12,2) DEFAULT '0.00',
  `seguro` tinyint(1) DEFAULT '0',
  `descripcion_contenido` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `web_services` tinyint(1) DEFAULT '0',
  `notas` varchar(255) DEFAULT NULL,
  `fecha_entrega` datetime DEFAULT NULL,
  `fecha_creacion` datetime DEFAULT CURRENT_TIMESTAMP,
  `fecha_actualizacion` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  `payload_solicitud` json DEFAULT NULL,
  PRIMARY KEY (`id_envio_cab`),
  KEY `idx_cliente` (`id_cliente`),
  KEY `idx_empresa` (`id_empresa_envio`),
  KEY `idx_estatus` (`cod_estatus_envio`),
  KEY `idx_guia_zoom` (`id_guia_zoom`),
  KEY `idx_referencia_interna` (`referencia_interna`),
  CONSTRAINT `tb_delivery_envio_cab_zoom_ibfk_1` FOREIGN KEY (`id_cliente`) REFERENCES `tb_delivery_cliente` (`id_cliente`),
  CONSTRAINT `tb_delivery_envio_cab_zoom_ibfk_2` FOREIGN KEY (`id_empresa_envio`) REFERENCES `tb_delivery_empresa_envio` (`id_empresa_envio`),
  CONSTRAINT `tb_delivery_envio_cab_zoom_ibfk_3` FOREIGN KEY (`cod_estatus_envio`) REFERENCES `tb_estatus_general` (`cod_estatus`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='La tabla tb_delivery_envio_cab_zoom almacena la información principal de los envíos generados a través del sistema de delivery, integrado con la plataforma Zoom, utilizada para logística y rastreo de paquetes.';

CREATE TABLE `tb_delivery_envio_cab_zoom_historico` (
  `id_envio_cab` int NOT NULL,
  `id_cliente` int NOT NULL,
  `id_empresa_envio` int NOT NULL,
  `cod_estatus_envio` int NOT NULL,
  `referencia_interna` varchar(50) NOT NULL,
  `id_guia_zoom` varchar(50) DEFAULT NULL,
  `referencia_zoom` varchar(50) DEFAULT NULL,
  `cod_cliente_zoom` int NOT NULL,
  `token_zoom` text,
  `certificado_zoom` text,
  `token_expiracion` datetime DEFAULT NULL,
  `remitente_nombre` varchar(100) NOT NULL,
  `contacto_remitente` varchar(100) DEFAULT NULL,
  `telefono_remitente` varchar(50) DEFAULT NULL,
  `remitente_direccion` text,
  `codciudad_remitente` int NOT NULL,
  `destinatario_nombre` varchar(100) NOT NULL,
  `contacto_destinatario` varchar(100) DEFAULT NULL,
  `telefono_destino` varchar(50) DEFAULT NULL,
  `destinatario_direccion` text,
  `codciudad_destinatario` int NOT NULL,
  `retira_oficina` tinyint(1) DEFAULT NULL,
  `cod_oficina_destino` int DEFAULT NULL,
  `codservicio_zoom` int NOT NULL,
  `tipo_tarifa` int DEFAULT NULL,
  `modalidad_tarifa` int DEFAULT NULL,
  `modalidad_cod` int DEFAULT NULL,
  `num_piezas` int DEFAULT NULL,
  `peso` decimal(10,3) NOT NULL,
  `alto` decimal(10,2) DEFAULT NULL,
  `ancho` decimal(10,2) DEFAULT NULL,
  `largo` decimal(10,2) DEFAULT NULL,
  `tipo_envio` char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `valor_mercancia` decimal(12,2) NOT NULL,
  `valor_declarado` decimal(12,2) DEFAULT NULL,
  `seguro` tinyint(1) DEFAULT NULL,
  `descripcion_contenido` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `web_services` tinyint(1) DEFAULT NULL,
  `notas` varchar(255) DEFAULT NULL,
  `fecha_entrega` datetime DEFAULT NULL,
  `fecha_creacion` datetime DEFAULT NULL,
  `fecha_actualizacion` datetime DEFAULT NULL,
  KEY `idx_cliente` (`id_cliente`),
  KEY `idx_empresa` (`id_empresa_envio`),
  KEY `idx_estatus` (`cod_estatus_envio`),
  KEY `idx_guia_zoom` (`id_guia_zoom`),
  KEY `idx_referencia_interna` (`referencia_interna`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='La tabla tb_delivery_envio_cab_zoom_historico almacena la información principal historica mayor a 1 mes de los envíos generados a través del sistema de delivery, integrado con la plataforma Zoom, utilizada para logística y rastreo de paquetes.';

CREATE TABLE `tb_delivery_envio_track_zoom` (
  `id_track_zoom` int NOT NULL AUTO_INCREMENT,
  `id_envio_cab` int NOT NULL,
  `id_guia_zoom` varchar(50) NOT NULL,
  `tipo_busqueda` int DEFAULT '1',
  `web_track` tinyint(1) DEFAULT '1',
  `cod_estatus_track` int NOT NULL COMMENT 'FK a tb_estatus_general (módulo: ZOOM_TRACK)',
  `track_nota` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT 'Observaciones específicas de este evento',
  `track_gps` varchar(50) DEFAULT NULL,
  `track_fechora` datetime NOT NULL,
  `fecha_registro` datetime DEFAULT CURRENT_TIMESTAMP,
  `payload_track_zoom` json DEFAULT NULL,
  `fecha_entrega` datetime DEFAULT NULL COMMENT 'indica la fecha de entrega del envio',
  PRIMARY KEY (`id_track_zoom`),
  KEY `idx_envio` (`id_envio_cab`),
  KEY `idx_guia` (`id_guia_zoom`),
  KEY `idx_fechora` (`track_fechora`),
  KEY `idx_estatus_track` (`cod_estatus_track`),
  KEY `idx_track_combinado` (`id_envio_cab`,`track_fechora` DESC),
  CONSTRAINT `tb_delivery_envio_track_zoom_ibfk_1` FOREIGN KEY (`id_envio_cab`) REFERENCES `tb_delivery_envio_cab_zoom` (`id_envio_cab`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `tb_delivery_envio_track_zoom_ibfk_2` FOREIGN KEY (`cod_estatus_track`) REFERENCES `tb_estatus_general` (`cod_estatus`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=30 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='La tabla tb_delivery_envio_track_zoom almacena el historial de rastreo (tracking) de los envíos gestionados a través de Zoom.';

CREATE TABLE `tb_delivery_envio_track_zoom_historico` (
  `id_track_zoom` int NOT NULL,
  `id_envio_cab` int NOT NULL,
  `id_guia_zoom` varchar(50) NOT NULL,
  `tipo_busqueda` int DEFAULT NULL,
  `web_track` tinyint(1) DEFAULT NULL,
  `cod_estatus_track` int NOT NULL COMMENT 'FK a tb_estatus_general (módulo: ZOOM_TRACK)',
  `track_nota` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT 'Observaciones específicas de este evento',
  `track_gps` varchar(50) DEFAULT NULL,
  `track_fechora` datetime NOT NULL,
  `fecha_registro` datetime DEFAULT NULL,
  `fecha_entrega` datetime DEFAULT NULL COMMENT 'indica la fecha de entrega del envio',
  KEY `id_track_zoom` (`id_track_zoom`),
  KEY `idx_envio` (`id_envio_cab`),
  KEY `idx_guia` (`id_guia_zoom`),
  KEY `idx_fechora` (`track_fechora`),
  KEY `idx_estatus_track` (`cod_estatus_track`),
  KEY `idx_track_combinado` (`id_envio_cab`,`track_fechora` DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='La tabla tb_delivery_envio_track_zoom almacena el historial de rastreo (tracking) de los envíos gestionados a través de Zoom.';

CREATE TABLE `tb_estatus_general` (
  `id_estatus_general` int NOT NULL AUTO_INCREMENT,
  `cod_estatus` int NOT NULL,
  `modulo_estatus` varchar(100) NOT NULL,
  `nombre_estatus` varchar(50) NOT NULL,
  `descripcion_estatus` varchar(255) NOT NULL,
  `fecha_creacion` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `bloqueo_estatus` tinyint(1) DEFAULT '0' COMMENT 'Indica si este estatus bloquea actualizaciones de otros estatus, se toma como ultimo estatus definitivo sin posibilidad a ninguna otra actualizacion.',
  PRIMARY KEY (`id_estatus_general`),
  UNIQUE KEY `uk_cod_mod` (`cod_estatus`,`modulo_estatus`),
  KEY `idx_modulo` (`modulo_estatus`),
  KEY `idx_codigo` (`cod_estatus`)
) ENGINE=InnoDB AUTO_INCREMENT=27 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Tabla que centraliza todos los estados del sistema, USO: Referencia para estatus de clientes, empresas, envíos, etc.\nEjemplo: cod_estatus=1 (ACTIVO), cod_estatus=2 (INACTIVO)\nmodulo_estatus: ''GENERAL'', ''ZOOM'', ''ARMI'', ''CLIENTE''\nnombre_estatus: ''ACTIVO'', ''RECIBIDA'', ''ENTREGADO'', etc.\nRelacionada con: Todas las tablas que tienen cod_estatus';

CREATE DEFINER=`root`@`localhost` PROCEDURE `LystoLocal`.`sp_actualizar_tracking_zoom`(
    IN p_id_envio_cab INT,
    IN p_cod_estatus_track INT,
    IN p_track_nota TEXT,
    IN p_payload JSON,
    OUT p_exito BOOLEAN,
    OUT p_mensaje VARCHAR(500)
)
BEGIN
    DECLARE v_id_guia_zoom VARCHAR(50);
    DECLARE v_estado_valido INT DEFAULT 0;
    DECLARE v_estado_entregado BOOLEAN DEFAULT FALSE;
    DECLARE v_cod_estatus_entregado INT;
    

    -- Manejador de excepciones
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET p_exito = FALSE;
        SET p_mensaje = 'ERROR: Excepción SQL en sp_actualizar_tracking_zoom';
        GET DIAGNOSTICS CONDITION 1
            p_mensaje = MESSAGE_TEXT;
    END;

    -- Iniciar transacción
    START TRANSACTION;
    -- Inicializar salidas
    SET p_exito = TRUE;
    SET p_mensaje = '';

    proc_label: BEGIN
    -- Validar si ya existe un registro con el mismo id_envio_cab y cod_estatus_track
    IF (SELECT COUNT(*) 
        FROM tb_delivery_envio_track_zoom 
        WHERE id_envio_cab = p_id_envio_cab 
          AND cod_estatus_track = p_cod_estatus_track) > 0 THEN

        SET p_exito = FALSE;
        SET p_mensaje = 'Error: Número de guía y estado ya registrados';
        ROLLBACK;
        LEAVE proc_label;

    END IF;    

        -- Validar que el estado ZOOM_TRACK exista en tb_estatus_general
        SELECT COUNT(*) INTO v_estado_valido 
        FROM tb_estatus_general 
        WHERE cod_estatus = p_cod_estatus_track 
          AND modulo_estatus = 'ENVIO';

        /*IF v_estado_valido = 0 THEN
            -- Asignar estado por defecto si no es válido
            SET p_cod_estatus_track = 1; -- CREADO
        END IF;*/

        -- Obtener el código de estatus que bloquea        
        if -- p_cod_estatus_track in 
        (select tb_estatus_general.bloqueo_estatus from tb_estatus_general 
        inner join tb_delivery_envio_track_zoom 
        on tb_estatus_general.cod_estatus = tb_delivery_envio_track_zoom.cod_estatus_track
        where tb_estatus_general.bloqueo_estatus = TRUE and tb_delivery_envio_track_zoom.id_envio_cab = p_id_envio_cab) = true then        
        	SET p_exito = FALSE;
            SET p_mensaje = 'Error: El envío tiene track de bloqueo dentro de sus estatus';
            ROLLBACK;
            LEAVE proc_label;
        end if;
        -- obtener el ultimo estatus para borrar los payload 
        

        -- Verificar si el estado actual es ENTREGADO
        IF p_cod_estatus_track in  (SELECT cod_estatus 
	        FROM tb_estatus_general 
	        WHERE  bloqueo_estatus = true
	          AND modulo_estatus = 'ENVIO')        
        THEN            
        	SET v_estado_entregado = TRUE;
        END IF;

        -- Obtener id_guia_zoom del envío
        SELECT id_guia_zoom INTO v_id_guia_zoom 
        FROM tb_delivery_envio_cab_zoom 
        WHERE id_envio_cab = p_id_envio_cab;

        -- Validar que se encontró la guía
        IF v_id_guia_zoom IS NULL THEN
            SET p_exito = FALSE;
            SET p_mensaje = 'Error: No se encontró la guía para el envío';
            ROLLBACK;
            LEAVE proc_label;
        END IF;

        -- Insertar nuevo registro de tracking
        INSERT INTO tb_delivery_envio_track_zoom (
            id_envio_cab,
            id_guia_zoom,
            tipo_busqueda,
            web_track,
            cod_estatus_track,
            track_nota,
            track_gps,
            track_fechora,
            fecha_registro,
            payload_track_zoom,
            fecha_entrega
        ) VALUES (
            p_id_envio_cab,
            v_id_guia_zoom,
            1,
            1,
            p_cod_estatus_track,
            p_track_nota,
            NULL,
            NOW(),
            NOW(),
            p_payload,
            now()
        );

        -- Limpiar payloads antiguos si el estado es ENTREGADO
        IF v_estado_entregado = TRUE THEN
            UPDATE tb_delivery_envio_track_zoom 
            SET payload_track_zoom = NULL 
            WHERE id_envio_cab = p_id_envio_cab;
              -- AND id_track_zoom != LAST_INSERT_ID();
        END IF;

        -- Limpiar payload en la cabecera si es ENTREGADO
        UPDATE tb_delivery_envio_cab_zoom 
        SET payload_solicitud = NULL,
        fecha_entrega = now()
        WHERE id_envio_cab = p_id_envio_cab;

        -- Éxito
        SET p_exito = TRUE;
        SET p_mensaje = CONCAT('Track actualizado exitosamente. Guía: ', v_id_guia_zoom, ' al estado: ', p_cod_estatus_track);

    END;

    COMMIT;

END;

CREATE DEFINER=`root`@`localhost` PROCEDURE `LystoLocal`.`sp_crear_envio_zoom`(
  IN p_id_cliente INT,
  IN p_id_empresa_envio INT,
  IN p_referencia_interna VARCHAR(50),
  -- IN p_num_guia_envio VARCHAR(50),
  IN p_token_zoom TEXT,
  IN p_certificado_zoom TEXT,
  IN p_codigo_cliente_zoom INT,
  
  -- Remitente
  IN p_remitente_nombre VARCHAR(100),
  IN p_remitente_direccion TEXT,
  IN p_codciudad_remitente INT,
  IN p_contacto_remitente VARCHAR(100),
  IN p_telefono_remitente VARCHAR(50),
  
  -- Destinatario
  IN p_destinatario_nombre VARCHAR(100),
  IN p_destinatario_direccion TEXT,
  IN p_codciudad_destinatario INT,
  IN p_contacto_destinatario VARCHAR(100),
  IN p_telefono_destino VARCHAR(50),
  
  -- Entrega
  IN p_retira_oficina BOOLEAN,
  IN p_cod_oficina_destino INT,
  
  -- Servicio
  IN p_codservicio_zoom INT,
  IN p_tipo_tarifa INT,
  IN p_modalidad_tarifa INT,
  IN p_modalidad_cod INT,
  
  -- Paquete
  IN p_num_piezas INT,
  IN p_peso DECIMAL(10,3),
  IN p_alto DECIMAL(10,2),
  IN p_ancho DECIMAL(10,2),
  IN p_largo DECIMAL(10,2),
  IN p_tipo_envio VARCHAR(1),
  IN p_valor_mercancia DECIMAL(12,2),
  IN p_valor_declarado DECIMAL(12,2),
  IN p_seguro BOOLEAN,
  IN p_descripcion_contenido TEXT,
  
  -- Sistema
  IN p_cod_estatus_envio INT,
  IN p_notas VARCHAR(255),
  IN p_referencia_zoom VARCHAR(50),
  IN p_id_guia_zoom VARCHAR(50),
  
  -- Backups
  IN p_payload_cab JSON,
  IN p_payload_track JSON,
  
  -- Out params
  OUT p_exito BOOLEAN,
  OUT p_mensaje VARCHAR(500)
)
BEGIN
  DECLARE v_id_envio_cab INT DEFAULT NULL;
  DECLARE v_cliente_existe INT DEFAULT 0;
  DECLARE v_guia_existe INT DEFAULT 0;
  DECLARE v_cod_track_inicial INT DEFAULT 100; -- CREADO en ZOOM_TRACK
  
  SET p_exito = FALSE;
  SET p_mensaje = '';

  -- Validaciones
  IF p_id_cliente IS NULL OR p_id_cliente <= 0 THEN
    SET p_mensaje = 'Error: ID de cliente inválido';
  END IF;

  /*IF p_num_guia_envio IS NULL OR p_num_guia_envio = '' THEN
    SET p_mensaje = CONCAT(p_mensaje, IF(p_mensaje != '', '; ', ''), 'Error: Número de guía es requerido');
  END IF;*/

  IF p_id_guia_zoom IS NULL OR p_id_guia_zoom = '' THEN
    SET p_mensaje = CONCAT(p_mensaje, IF(p_mensaje != '', '; ', ''), 'Error: ID de guía Zoom es requerido');
  END IF;
  
  -- validar que empresa emvio existe
  IF (select count(*) from tb_delivery_empresa_envio e 
  where e.id_empresa_envio = p_id_empresa_envio) = 0 then
  	SET p_mensaje = CONCAT(p_mensaje, IF(p_mensaje != '', '; ', ''), 'Error: Empresa de envio inexistente');
  end if;
  
  -- Validar que el estado ENVIO existe
  IF p_cod_estatus_envio IS NOT NULL THEN
    SELECT COUNT(*) INTO v_cliente_existe
    FROM tb_estatus_general 
    WHERE cod_estatus = p_cod_estatus_envio 
      AND modulo_estatus = 'ENVIO';
    
    IF v_cliente_existe = 0 THEN
      SET p_mensaje = CONCAT(p_mensaje, IF(p_mensaje != '', '; ', ''), 'Error: Código de estado ENVIO inválido');
      SET p_cod_estatus_envio = 1; -- Default a CREADO
    END IF;
  ELSE
    SET p_cod_estatus_envio = 1; -- Default a CREADO
  END IF;
  
  -- Verificar cliente
  IF p_mensaje = '' THEN
    SELECT COUNT(*) INTO v_cliente_existe 
    FROM tb_delivery_cliente 
    WHERE id_cliente = p_id_cliente;
    
    IF v_cliente_existe = 0 THEN
      SET p_mensaje = 'Error: El cliente no existe';
    END IF;
  END IF;
  
  -- Verificar guía
  IF p_mensaje = '' THEN
    SELECT COUNT(*) INTO v_guia_existe 
    FROM tb_delivery_envio_cab_zoom 
    WHERE id_guia_zoom = p_id_guia_zoom;
    
    IF v_guia_existe > 0 THEN
      SET p_mensaje = 'Error: Número de guía existente';
    END IF;
  END IF;

  -- Si hay errores, salir
  IF p_mensaje != '' THEN
    SET p_exito = FALSE;
  ELSE
    -- Iniciar transacción
    START TRANSACTION;
    
    BEGIN
      -- DECLARE EXIT HANDLER FOR SQLEXCEPTION
      BEGIN
        ROLLBACK;
        SET p_exito = FALSE;
        SET p_mensaje = 'Error en operación SQL, procedimiento almacenado: sp_crear_envio_zoom';
      END;
      
      -- Insertar en cabecera
      INSERT INTO tb_delivery_envio_cab_zoom (
        id_cliente,
        id_empresa_envio,
        cod_estatus_envio,
        referencia_interna,
        -- num_guia_envio,
        id_guia_zoom,
        referencia_zoom,
        cod_cliente_zoom,
        token_zoom,
        certificado_zoom,
        token_expiracion,
        remitente_nombre,
        contacto_remitente,
        telefono_remitente,
        remitente_direccion,
        codciudad_remitente,
        destinatario_nombre,
        contacto_destinatario,
        telefono_destino,
        destinatario_direccion,
        codciudad_destinatario,
        retira_oficina,
        cod_oficina_destino,
        codservicio_zoom,
        tipo_tarifa,
        modalidad_tarifa,
        modalidad_cod,
        num_piezas,
        peso,
        alto,
        ancho,
        largo,
        tipo_envio,
        valor_mercancia,
        valor_declarado,
        seguro,
        descripcion_contenido,
        web_services,
        notas,
        fecha_envio,
        payload_solicitud
      ) VALUES (
        p_id_cliente,
        p_id_empresa_envio,
        IFNULL(p_cod_estatus_envio, 1),
        p_referencia_interna,
        -- p_num_guia_envio,
        p_id_guia_zoom,
        p_referencia_zoom,
        IFNULL(p_codigo_cliente_zoom, 407940),
        p_token_zoom,
        p_certificado_zoom,
        NULL,
        p_remitente_nombre,
        IFNULL(p_contacto_remitente, p_remitente_nombre),
        p_telefono_remitente,
        p_remitente_direccion,
        p_codciudad_remitente,
        p_destinatario_nombre,
        IFNULL(p_contacto_destinatario, p_destinatario_nombre),
        p_telefono_destino,
        p_destinatario_direccion,
        p_codciudad_destinatario,
        IFNULL(p_retira_oficina, FALSE),
        p_cod_oficina_destino,
        IFNULL(p_codservicio_zoom, 104),
        IFNULL(p_tipo_tarifa, 1),
        IFNULL(p_modalidad_tarifa, 2),
        p_modalidad_cod,
        IFNULL(p_num_piezas, 1),
        p_peso,
        p_alto,
        p_ancho,
        p_largo,
        IFNULL(p_tipo_envio, 'M'),
        p_valor_mercancia,
        IFNULL(p_valor_declarado, 0.00),
        IFNULL(p_seguro, FALSE),
        p_descripcion_contenido,
        1,
        p_notas,
        NOW(),
        IFNULL(p_payload_cab, JSON_OBJECT('source', 'sp_crear_envio_zoom'))
      );
      
      SET v_id_envio_cab = LAST_INSERT_ID();
      
      -- Insertar tracking inicial (usando ZOOM_TRACK código 100 = CREADO)
      INSERT INTO tb_delivery_envio_track_zoom (
        id_envio_cab,
        id_guia_zoom,
        tipo_busqueda,
        web_track,
        cod_estatus_track,
        track_nota,
        track_gps,
        track_fechora,
        fecha_registro,
        payload_track_zoom
      ) VALUES (
        v_id_envio_cab,
        p_id_guia_zoom,
        1,
        1,
        1, -- CREADO en ZOOM_TRACK
        CONCAT('Envío creado. Referencia interna: ', p_referencia_interna),
        NULL,
        NOW(),
        NOW(),
        IFNULL(p_payload_track, JSON_OBJECT('source', 'sp_crear_envio_zoom'))
      );
      
      -- COMMIT;
      
      SET p_exito = TRUE;
      SET p_mensaje = CONCAT('Envío creado exitosamente. ID: ', v_id_envio_cab);
      
    END;
  END IF;
  IF (SELECT @@error_count) > 0 THEN
    ROLLBACK;
  ELSE
    COMMIT;
  END IF;
END;

CREATE DEFINER=`root`@`localhost` PROCEDURE `LystoLocal`.`sp_guarda_cliente_zoom`(
  IN p_tipo_cliente VARCHAR(20),
  IN p_tipo_documento CHAR(1),
  IN p_num_documento VARCHAR(10),
  IN p_telefono VARCHAR(14),
  IN p_mail VARCHAR(50),
  IN p_direccion VARCHAR(200),
  IN p_cod_cliente_zoom INT  
)
BEGIN
  DECLARE v_id_cliente INT;

  -- Fallback de tipo_cliente
  IF p_tipo_cliente IS NULL OR p_tipo_cliente = '' THEN
    SET p_tipo_cliente = 'CLIENTE_FINAL';
  END IF;

  -- Buscar existente
  SELECT id_cliente
    INTO v_id_cliente
    FROM tb_delivery_cliente
   WHERE tipo_documento = p_tipo_documento
     AND num_documento = p_num_documento
   LIMIT 1;

  IF v_id_cliente IS NULL THEN
    INSERT INTO tb_delivery_cliente (
      tipo_cliente, tipo_documento, num_documento,
      telefono, mail, direccion,
      cod_cliente_zoom, 
      cod_estatus_cliente
    ) VALUES (
      p_tipo_cliente, p_tipo_documento, p_num_documento,
      p_telefono, p_mail, p_direccion,
      p_cod_cliente_zoom, 
      1
    );
    SET v_id_cliente = LAST_INSERT_ID();
  ELSE
    UPDATE tb_delivery_cliente
       SET tipo_cliente = p_tipo_cliente,
         telefono = p_telefono,
         mail = p_mail,
         direccion = p_direccion,
         cod_cliente_zoom = p_cod_cliente_zoom,         
         fecha_actualizacion = NOW()
     WHERE id_cliente = v_id_cliente;
  END IF;

  SELECT v_id_cliente AS id_cliente;
END;

CREATE EVENT zoom_historico
ON SCHEDULE EVERY 1 DAY
STARTS '2025-12-15 15:25:04.000'
ON COMPLETION NOT PRESERVE
ENABLE
DO BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION;

    -- Cabeceras
    CREATE TEMPORARY TABLE temp 
	SELECT id_envio_cab FROM tb_delivery_envio_cab_zoom
	WHERE fecha_entrega < DATE_SUB(CURDATE(), INTERVAL 1 MONTH); -- 1 MINUTE);  1 MONTH);

    
    INSERT INTO tb_delivery_envio_cab_zoom_historico 
	SELECT
		tb_delivery_envio_cab_zoom.id_envio_cab,
		id_cliente,
		id_empresa_envio,
		cod_estatus_envio,
		referencia_interna,
		id_guia_zoom,
		referencia_zoom,
		cod_cliente_zoom,
		token_zoom,
		certificado_zoom,
		token_expiracion,
		remitente_nombre,
		contacto_remitente,
		telefono_remitente,
		remitente_direccion,
		codciudad_remitente,
		destinatario_nombre,
		contacto_destinatario,
		telefono_destino,
		destinatario_direccion,
		codciudad_destinatario,
		retira_oficina,
		cod_oficina_destino,
		codservicio_zoom,
		tipo_tarifa,
		modalidad_tarifa,
		modalidad_cod,
		num_piezas,
		peso,
		alto,
		ancho,
		largo,
		tipo_envio,
		valor_mercancia,
		valor_declarado,
		seguro,
		descripcion_contenido,
		web_services,
		notas,
		fecha_entrega,
		fecha_creacion,
		fecha_actualizacion
	FROM
		tb_delivery_envio_cab_zoom
	inner join temp on
		tb_delivery_envio_cab_zoom.id_envio_cab = temp.id_envio_cab;
    
       

    -- Tracking
    INSERT
	INTO
	tb_delivery_envio_track_zoom_historico
    SELECT
		id_track_zoom,
		tb_delivery_envio_track_zoom.id_envio_cab,
		id_guia_zoom,
		tipo_busqueda,
		web_track,
		cod_estatus_track,
		track_nota,
		track_gps,
		track_fechora,
		fecha_registro,
		fecha_entrega
	FROM
		tb_delivery_envio_track_zoom
	inner join temp on
		tb_delivery_envio_track_zoom.id_envio_cab = temp.id_envio_cab;
    
    /*
	select * from temp;
    select * from tb_delivery_envio_cab_zoom_historico;
    select * from tb_delivery_envio_cab_zoom;
    select * from tb_delivery_envio_track_zoom_historico;
    select * from tb_delivery_envio_track_zoom
    */
    -- borrado de cabecera
    DELETE
	tb_delivery_envio_cab_zoom
	FROM
		tb_delivery_envio_cab_zoom
	inner join temp
	    on
		tb_delivery_envio_cab_zoom.id_envio_cab = temp.id_envio_cab;

    -- borrado de tracking
	DELETE
	tb_delivery_envio_track_zoom
	FROM
		tb_delivery_envio_track_zoom
	INNER JOIN temp ON
		tb_delivery_envio_track_zoom.id_envio_cab = temp.id_envio_cab;   
	
    -- si no hay errores hacer el commit
    COMMIT;
END;
-- ============================================
-- 10. SCRIPT DE PRUEBA CON NUEVA ESTRUCTURA
-- ============================================

-- A. PRUEBA 1: Crear envío
SET @exito = FALSE;
SET @mensaje = '';

CALL sp_crear_envio_zoom(
  /* p_id_cliente */             1,
  /* p_id_empresa_envio */       3,
  /* p_referencia_interna */     'TEST-NORM-001',
  /* p_num_guia_envio */         'GUIA-NORM-001',
  /* p_token_zoom */             'token_norm',
  /* p_certificado_zoom */       'cert_norm',
  /* p_codigo_cliente_zoom */    407940,
  
  /* Remitente */
  /* p_remitente_nombre */       'Test Normalizado',
  /* p_remitente_direccion */    'Dirección Test',
  /* p_codciudad_remitente */    19,
  /* p_contacto_remitente */     'Contacto R',
  /* p_telefono_remitente */     '0412-1111111',
  
  /* Destinatario */
  /* p_destinatario_nombre */    'Destino Test',
  /* p_destinatario_direccion */ 'Destino 123',
  /* p_codciudad_destinatario */ 46,
  /* p_contacto_destinatario */  'Contacto D',
  /* p_telefono_destino */       '0414-2222222',
  
  /* Entrega */
  /* p_retira_oficina */         FALSE,
  /* p_cod_oficina_destino */    NULL,
  
  /* Servicio */
  /* p_codservicio_zoom */       104,
  /* p_tipo_tarifa */            1,
  /* p_modalidad_tarifa */       2,
  /* p_modalidad_cod */          NULL,
  
  /* Paquete */
  /* p_num_piezas */             1,
  /* p_peso */                   2.5,
  /* p_alto */                   15.0,
  /* p_ancho */                  25.0,
  /* p_largo */                  35.0,
  /* p_tipo_envio */             'M',
  /* p_valor_mercancia */        300.00,
  /* p_valor_declarado */        250.00,
  /* p_seguro */                 FALSE,
  /* p_descripcion_contenido */  'Prueba normalización',
  
  /* Sistema */
  /* p_cod_estatus_envio */      1,  -- CREADO
  /* p_notas */                  'Prueba estructura normalizada',
  /* p_referencia_zoom */        'REF-NORM-001',
  /* p_id_guia_zoom */           'ZOOM-NORM-001',
  
  /* Backups */
  /* p_payload_cab */            JSON_OBJECT('test', 'normalizado'),
  /* p_payload_track */          JSON_OBJECT('payload', 'inicial', 'pesado', REPEAT('x', 1000)),
  
  /* Out params */
  @exito,
  @mensaje
);

SELECT @exito AS exito_creacion, @mensaje AS mensaje_creacion;

-- B. Ver envío creado
SELECT 
    e.id_envio_cab,
    e.referencia_interna,
    e.num_guia_envio,
    e.id_guia_zoom,
    e.cod_estatus_envio,
    es.nombre_estatus AS estado_envio,
    e.fecha_creacion
FROM tb_delivery_envio_cab_zoom e
JOIN tb_estatus_general es ON e.cod_estatus_envio = es.cod_estatus
WHERE e.id_guia_zoom = 'ZOOM-NORM-001';

-- C. Ver tracking inicial CON JOIN NORMALIZADO ✅
SELECT 
    t.track_fechora,
    es.nombre_estatus AS estado,
    es.descripcion_estatus AS descripcion,
    t.track_nota,
    LENGTH(t.payload_track_zoom) AS tamano_payload
FROM tb_delivery_envio_track_zoom t
JOIN tb_estatus_general es ON t.cod_estatus_track = es.cod_estatus
WHERE t.id_guia_zoom = 'ZOOM-NORM-001'
ORDER BY t.track_fechora DESC;

-- D. PRUEBA 2: Actualizar tracking (En tránsito) - código 104
SET @id_envio = (SELECT id_envio_cab FROM tb_delivery_envio_cab_zoom WHERE id_guia_zoom = 'ZOOM-NORM-001' LIMIT 1);

CALL sp_actualizar_tracking_zoom(
  @id_envio,
  104,  -- ZOOM_TRACK.EN TRANSITO
  'El paquete está en camino',
  JSON_OBJECT('evento', 'en_transito', 'datos', REPEAT('y', 500))
);

-- E. PRUEBA 3: Actualizar tracking (Entregado) - código 107 ¡LIMPIARÁ PAYLOADS!
CALL sp_actualizar_tracking_zoom(
  @id_envio,
  107,  -- ZOOM_TRACK.ENTREGADO
  'Paquete entregado exitosamente',
  JSON_OBJECT('evento', 'entregado', 'datos', REPEAT('z', 800))
);

-- F. Ver TODOS los tracks con JOIN y verificar limpieza
SELECT 
    DATE_FORMAT(t.track_fechora, '%d/%m/%Y %H:%i') AS fecha_hora,
    es.nombre_estatus AS estado,
    es.descripcion_estatus AS descripcion,
    t.track_nota,
    CASE 
        WHEN t.payload_track_zoom IS NULL THEN '✅ LIMPIADO'
        ELSE CONCAT('❌ ', LENGTH(t.payload_track_zoom), ' bytes')
    END AS payload_status,
    e.cod_estatus_envio AS estado_actual_envio,
    es2.nombre_estatus AS estado_envio_texto
FROM tb_delivery_envio_track_zoom t
JOIN tb_estatus_general es ON t.cod_estatus_track = es.cod_estatus
JOIN tb_delivery_envio_cab_zoom e ON t.id_envio_cab = e.id_envio_cab
JOIN tb_estatus_general es2 ON e.cod_estatus_envio = es2.cod_estatus
WHERE t.id_guia_zoom = 'ZOOM-NORM-001'
ORDER BY t.track_fechora ASC;

-- G. Ver estado final
SELECT 
    e.id_envio_cab,
    e.referencia_interna,
    e.num_guia_envio,
    e.cod_estatus_envio,
    es.nombre_estatus AS estado_final,
    COUNT(t.id_track_zoom) AS total_tracks,
    SUM(CASE WHEN t.payload_track_zoom IS NULL THEN 1 ELSE 0 END) AS payloads_limpiados
FROM tb_delivery_envio_cab_zoom e
JOIN tb_estatus_general es ON e.cod_estatus_envio = es.cod_estatus
LEFT JOIN tb_delivery_envio_track_zoom t ON e.id_envio_cab = t.id_envio_cab
WHERE e.id_guia_zoom = 'ZOOM-NORM-001'
GROUP BY e.id_envio_cab;






