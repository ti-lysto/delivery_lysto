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
        fecha_creacion,
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

------------------------------------ARMI------------------------------------------------------
-- Tabla principal de envíos (modificada)
CREATE TABLE IF NOT EXISTS tb_delivery_envio_ARMI (
    id_envio BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT 'ID interno único del envío',
    business_id BIGINT NOT NULL COMMENT 'ID del negocio al que pertenece la orden (BusinessId)',
    total_value DOUBLE NOT NULL COMMENT 'Valor total de la orden (suma de productos + delivery + propinas, etc.)',
    user_tip DOUBLE DEFAULT 0.00 COMMENT 'Propina opcional entregada por el usuario para el repartidor',
    incentive_value DOUBLE DEFAULT 0.00 COMMENT 'Incentivo extra entregado por la empresa o plataforma',
    delivery_value DOUBLE NOT NULL COMMENT 'Costo del servicio de entrega',
    vehicle_type INT NOT NULL COMMENT 'Tipo de vehículo requerido (1 = bicicleta, 2 = moto, 3 = carro)',
    payment_method INT NOT NULL COMMENT 'Método de pago (1 = efectivo, 2 = Datafono, 3 = transferencia)',
    weight DOUBLE NOT NULL COMMENT 'Peso total de los productos (en kilogramos)',
    city VARCHAR(100) NOT NULL COMMENT 'Ciudad en la que se realiza la entrega',
    instructions TEXT COMMENT 'Instrucciones adicionales para el repartidor (puede estar vacío)',
    orderInvoice VARCHAR(100) COMMENT 'Código o referencia de factura de la orden (opcional o contable)',
    token VARCHAR(255) COMMENT 'Token para validar/reintentar de forma segura (puede estar vacío)',
    first_name VARCHAR(100) NOT NULL COMMENT 'Nombre del cliente',
    last_name VARCHAR(100) NOT NULL COMMENT 'Apellido del cliente',
    phone VARCHAR(50) NOT NULL COMMENT 'Número de teléfono del cliente',
    email VARCHAR(150) COMMENT 'Dirección de correo electrónico del cliente',
    address TEXT NOT NULL COMMENT 'Dirección física de entrega',
    lat DOUBLE COMMENT 'Latitud de la dirección de entrega',
    lng DOUBLE COMMENT 'Longitud de la dirección de entrega',
    dni VARCHAR(50) COMMENT 'Número de identificación del cliente (cédula, etc.)',
    orden_status INT DEFAULT 0 COMMENT 'Estatus de la orden',
    cancelado TINYINT(1) DEFAULT 0 COMMENT 'Indica si la orden fue cancelada (0 = no, 1 = sí)',
    fecha_cancelacion DATETIME COMMENT 'Fecha y hora de cancelación de la orden',
    motivo_cancelacion VARCHAR(500) COMMENT 'Motivo de la cancelación',
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Fecha y hora de creación del registro',
    fecha_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Fecha y hora de última actualización',
    fecha_entrega DATETIME COMMENT 'Fecha y hora de entrega del pedido',
    nota_interna TEXT COMMENT 'Nota interna para comentarios administrativos',
    instaleap_payload JSON COMMENT 'JSON recibido de la API Instaleap',
    armi_payload JSON COMMENT 'JSON recibido de la API ARMI',
    
    -- Índices para mejorar rendimiento
    INDEX idx_business_id (business_id),
    INDEX idx_city (city),
    INDEX idx_fecha_creacion (fecha_creacion),
    INDEX idx_payment_method (payment_method),
    INDEX idx_cancelado (cancelado),
    INDEX idx_fecha_entrega (fecha_entrega),
    INDEX idx_token (token(50))
) COMMENT='Tabla principal de envíos de delivery';

-- Tabla de productos del envío
CREATE TABLE IF NOT EXISTS tb_delivery_productosenvio_ARMI (
    id_producto_envio BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT 'ID interno único del producto en el envío',
    id_envio BIGINT NOT NULL COMMENT 'ID del envío relacionado (FK a tb_delivery_envio_ARMI)',
    product_id BIGINT NULL COMMENT 'ID del producto en la tienda (opcional). Si es nulo, se autoincrementa por envío',
    name VARCHAR(200) NOT NULL COMMENT 'Nombre del producto',
    description TEXT COMMENT 'Descripción breve del producto',
    quantity BIGINT NOT NULL COMMENT 'Cantidad solicitada',
    image_url VARCHAR(500) COMMENT 'URL de imagen representativa del producto',
    unit_price DOUBLE NOT NULL COMMENT 'Precio unitario del producto',
    store_id BIGINT NOT NULL COMMENT 'ID de la tienda donde se adquiere el producto (BranchOfficeId)',
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Fecha y hora de creación del registro',
    
    -- Clave foránea para relación con la tabla de envíos
    FOREIGN KEY (id_envio) REFERENCES tb_delivery_envio_ARMI(id_envio) ON DELETE CASCADE,
    
    -- Índices para mejorar rendimiento
    INDEX idx_id_envio (id_envio),
    INDEX idx_product_id (product_id),
    INDEX idx_store_id (store_id),
    INDEX idx_fecha_creacion (fecha_creacion),
    INDEX idx_name (name(100))
) COMMENT='Tabla de productos incluidos en cada envío';

CREATE TABLE IF NOT EXISTS tb_delivery_tracking_ARMI (
    id_tracking BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT 'ID interno único del registro de tracking',
    -- Relación con la tabla principal de envíos
    id_envio BIGINT NOT NULL COMMENT 'ID del envío relacionado (FK a tb_delivery_envio_ARMI)',    
    -- Información del estado
    estado_id INT NOT NULL COMMENT 'ID numérico del estado (según catálogo interno)',
    estado_nombre VARCHAR(50) NOT NULL COMMENT 'Nombre del estado (ej: ENTREGADA, CANCELADA, EN CAMINO)',
    estado_descripcion VARCHAR(500) COMMENT 'Descripción detallada del estado',
    -- Información de ubicación (cuando aplique)
    latitud DOUBLE COMMENT 'Latitud de la ubicación en el momento del estado',
    longitud DOUBLE COMMENT 'Longitud de la ubicación en el momento del estado',
    -- Información temporal
    fecha_estado DATETIME NOT NULL COMMENT 'Fecha y hora en que se produjo el estado',        
    -- Índices para optimización
    INDEX idx_id_envio (id_envio),
    INDEX idx_estado_id (estado_id),
    INDEX idx_estado_nombre (estado_nombre),
    INDEX idx_fecha_estado (fecha_estado),    
    -- Clave foránea para integridad referencial
    FOREIGN KEY (id_envio) 
        REFERENCES tb_delivery_envio_ARMI(id_envio) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE
    
)COMMENT='Tabla de historial de tracking de estados de envíos (ARMI y otros sistemas)';

-- ============================================
-- PROCEDIMIENTOS ALMACENADOS 
-- ============================================

DELIMITER $$

-- Procedimiento para insertar un envío con manejo robusto de errores
CREATE PROCEDURE sp_insertar_envio_completo_ARMI(
    -- Parámetros de entrada
    IN p_business_id BIGINT,
    IN p_total_value DOUBLE,
    IN p_user_tip DOUBLE,
    IN p_incentive_value DOUBLE,
    IN p_delivery_value DOUBLE,
    IN p_vehicle_type INT,
    IN p_payment_method INT,
    IN p_weight DOUBLE,
    IN p_city VARCHAR(100),
    IN p_instructions TEXT,
    IN p_orderInvoice VARCHAR(100),
    IN p_token VARCHAR(255),
    IN p_first_name VARCHAR(100),
    IN p_last_name VARCHAR(100),
    IN p_phone VARCHAR(50),
    IN p_email VARCHAR(150),
    IN p_address TEXT,
    IN p_lat DOUBLE,
    IN p_lng DOUBLE,
    IN p_dni VARCHAR(50),
    IN p_nota_interna TEXT,
    IN p_instaleap_payload JSON,
    IN p_armi_payload JSON,
    -- Parámetros de salida
    OUT p_exito BOOLEAN,
    OUT p_mensaje VARCHAR(500),
    OUT p_id_envio_generado BIGINT
)
proc_insertar: BEGIN
    -- Variables locales - deben declararse al inicio
    DECLARE v_error_code CHAR(5) DEFAULT '00000';
    DECLARE v_error_message VARCHAR(500);
    DECLARE v_existing_token INT DEFAULT 0;
    DECLARE v_max_retries INT DEFAULT 3;
    DECLARE v_retry_count INT DEFAULT 0;
    DECLARE v_success BOOLEAN DEFAULT FALSE;
    
    -- Declarar handler de errores
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        GET DIAGNOSTICS CONDITION 1
            v_error_code = RETURNED_SQLSTATE,
            v_error_message = MESSAGE_TEXT;
        
        SET p_exito = FALSE;
        SET p_mensaje = CONCAT('Error SQL: ', v_error_code, ' - ', v_error_message);
        
    END;
    
    -- Inicializar parámetros de salida
    SET p_exito = FALSE;
    SET p_mensaje = '';
    SET p_id_envio_generado = NULL;
    
    -- Validaciones de entrada
    IF p_business_id IS NULL OR p_business_id <= 0 THEN
        SET p_mensaje = 'El business_id es requerido y debe ser mayor a 0';
        SET p_exito = FALSE;
        LEAVE proc_insertar;
    END IF;
    
    IF p_total_value IS NULL OR p_total_value < 0 THEN
        SET p_mensaje = 'El total_value es requerido y no puede ser negativo';
        SET p_exito = FALSE;
        LEAVE proc_insertar;
    END IF;
    
    IF p_delivery_value IS NULL OR p_delivery_value < 0 THEN
        SET p_mensaje = 'El delivery_value es requerido y no puede ser negativo';
        SET p_exito = FALSE;
        LEAVE proc_insertar;
    END IF;
    
    IF p_vehicle_type NOT IN (1, 2, 3) THEN
        SET p_mensaje = 'El vehicle_type debe ser 1 (bicicleta), 2 (moto) o 3 (carro)';
        SET p_exito = FALSE;
        LEAVE proc_insertar;
    END IF;
    
    IF p_payment_method NOT IN (1, 2, 3) THEN
        SET p_mensaje = 'El payment_method debe ser 1 (efectivo), 2 (Datafono) o 3 (transferencia)';
        SET p_exito = FALSE;
        LEAVE proc_insertar;
    END IF;
    
    IF p_city IS NULL OR TRIM(p_city) = '' THEN
        SET p_mensaje = 'La ciudad es requerida';
        SET p_exito = FALSE;
        LEAVE proc_insertar;
    END IF;
    
    IF p_first_name IS NULL OR TRIM(p_first_name) = '' THEN
        SET p_mensaje = 'El nombre del cliente es requerido';
        SET p_exito = FALSE;
        LEAVE proc_insertar;
    END IF;
    
    IF p_phone IS NULL OR TRIM(p_phone) = '' THEN
        SET p_mensaje = 'El teléfono del cliente es requerido';
        SET p_exito = FALSE;
        LEAVE proc_insertar;
    END IF;
    
    IF p_address IS NULL OR TRIM(p_address) = '' THEN
        SET p_mensaje = 'La dirección de entrega es requerida';
        SET p_exito = FALSE;
        LEAVE proc_insertar;
    END IF;
    
    -- Validar token único si se proporciona
    IF p_token IS NOT NULL AND TRIM(p_token) != '' THEN
        SELECT COUNT(*) INTO v_existing_token 
        FROM tb_delivery_envio_ARMI 
        WHERE token = p_token;
        
        IF v_existing_token > 0 THEN
            SET p_mensaje = CONCAT('El token ya existe en el sistema: ', p_token);
            SET p_exito = FALSE;
            LEAVE proc_insertar;
        END IF;
    END IF;
    
    -- Validar JSON payloads
    IF p_instaleap_payload IS NOT NULL AND NOT JSON_VALID(p_instaleap_payload) THEN
        SET p_mensaje = 'El payload de Instaleap no es un JSON válido';
        SET p_exito = FALSE;
        LEAVE proc_insertar;
    END IF;
    
    IF p_armi_payload IS NOT NULL AND NOT JSON_VALID(p_armi_payload) THEN
        SET p_mensaje = 'El payload de ARMI no es un JSON válido';
        SET p_exito = FALSE;
        LEAVE proc_insertar;
    END IF;
    
    -- Intentar inserción con reintentos
    SET v_retry_count = 0;
    SET v_success = FALSE;
    
    WHILE v_retry_count < v_max_retries AND NOT v_success DO
        BEGIN
            DECLARE EXIT HANDLER FOR 1062 BEGIN -- Duplicate entry
                SET v_retry_count = v_retry_count + 1;
                IF v_retry_count >= v_max_retries THEN
                    SET p_mensaje = 'Error de duplicado después de múltiples intentos';
                    SET p_exito = FALSE;
                END IF;
            END;
            
            -- Insertar en la tabla principal
            INSERT INTO tb_delivery_envio_ARMI (
                business_id, total_value, user_tip, incentive_value, 
                delivery_value, vehicle_type, payment_method, weight, 
                city, instructions, orderInvoice, token, first_name, 
                last_name, phone, email, address, lat, lng, dni,
                nota_interna, instaleap_payload, armi_payload
            ) VALUES (
                p_business_id, p_total_value, 
                COALESCE(p_user_tip, 0.00), 
                COALESCE(p_incentive_value, 0.00),
                p_delivery_value, p_vehicle_type, p_payment_method, 
                COALESCE(p_weight, 0.00),
                TRIM(p_city), p_instructions, p_orderInvoice, p_token, 
                TRIM(p_first_name), TRIM(p_last_name), TRIM(p_phone), 
                p_email, TRIM(p_address), p_lat, p_lng, p_dni,
                p_nota_interna, p_instaleap_payload, p_armi_payload
            );
            
            -- Obtener el ID del envío insertado
            SET p_id_envio_generado = LAST_INSERT_ID();
            SET v_success = TRUE;
        END;
    END WHILE;
    
    -- Verificar éxito de la operación
    IF v_success THEN
        SET p_exito = TRUE;
        SET p_mensaje = CONCAT('Envío creado exitosamente con ID: ', p_id_envio_generado);
    ELSEIF p_mensaje = '' THEN
        SET p_mensaje = 'Error desconocido al crear el envío';
    END IF;
    
END$$

-- Procedimiento para actualizar fecha de entrega con manejo de errores
CREATE PROCEDURE sp_actualizar_fecha_entrega_ARMI(
    -- Parámetros de entrada
    IN p_id_envio BIGINT,
    IN p_fecha_entrega DATETIME,
    -- Parámetros de salida
    OUT p_exito BOOLEAN,
    OUT p_mensaje VARCHAR(500)
)
proc_actualizar_fecha: BEGIN
    -- Variables locales - deben declararse al inicio
    DECLARE v_error_code CHAR(5) DEFAULT '00000';
    DECLARE v_error_message VARCHAR(500);
    DECLARE v_existe INT DEFAULT 0;
    DECLARE v_cancelado INT DEFAULT 0;
    DECLARE v_ya_entregado INT DEFAULT 0;
    DECLARE v_fecha_actual DATETIME;
    
    -- Declarar handler de errores
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        GET DIAGNOSTICS CONDITION 1
            v_error_code = RETURNED_SQLSTATE,
            v_error_message = MESSAGE_TEXT;
        
        SET p_exito = FALSE;
        SET p_mensaje = CONCAT('Error SQL: ', v_error_code, ' - ', v_error_message);
    END;
    
    -- Inicializar parámetros de salida
    SET p_exito = FALSE;
    SET p_mensaje = '';
    
    -- Validaciones de entrada
    IF p_id_envio IS NULL OR p_id_envio <= 0 THEN
        SET p_mensaje = 'El ID del envío es requerido y debe ser mayor a 0';
        SET p_exito = FALSE;
        LEAVE proc_actualizar_fecha;
    END IF;
    
    IF p_fecha_entrega IS NULL THEN
        SET p_mensaje = 'La fecha de entrega es requerida';
        SET p_exito = FALSE;
        LEAVE proc_actualizar_fecha;
    END IF;
    
    -- Verificar si la fecha de entrega es futura (validación opcional)
    IF p_fecha_entrega > NOW() THEN
        SET p_mensaje = 'Advertencia: La fecha de entrega es futura';
        -- No se bloquea, solo se advierte
    END IF;
    
    -- Verificar si el envío existe y obtener su estado
    SELECT 
        COUNT(*),
        COALESCE(cancelado, 0),
        CASE WHEN fecha_entrega IS NOT NULL THEN 1 ELSE 0 END,
        fecha_entrega
    INTO 
        v_existe,
        v_cancelado,
        v_ya_entregado,
        v_fecha_actual
    FROM tb_delivery_envio_ARMI 
    WHERE id_envio = p_id_envio;
    
    IF v_existe = 0 THEN
        SET p_mensaje = CONCAT('El envío con ID ', p_id_envio, ' no existe');
        SET p_exito = FALSE;
        LEAVE proc_actualizar_fecha;
    END IF;
    
    -- Validar estado del envío
    IF v_cancelado = 1 THEN
        SET p_mensaje = CONCAT('No se puede actualizar fecha de entrega. El envío ', p_id_envio, ' está cancelado');
        SET p_exito = FALSE;
        LEAVE proc_actualizar_fecha;
    END IF;
    
    IF v_ya_entregado = 1 THEN
        -- Verificar si ya tiene la misma fecha
        IF v_fecha_actual = p_fecha_entrega THEN
            SET p_mensaje = CONCAT('El envío ', p_id_envio, ' ya tiene esta fecha de entrega');
            SET p_exito = TRUE; -- Se considera éxito porque no hay cambio
            LEAVE proc_actualizar_fecha;
        ELSE
            SET p_mensaje = CONCAT('El envío ', p_id_envio, ' ya fue entregado el ', 
                                  DATE_FORMAT(v_fecha_actual, '%Y-%m-%d %H:%i:%s'));
            SET p_exito = FALSE;
            LEAVE proc_actualizar_fecha;
        END IF;
    END IF;
    
    -- Actualizar fecha de entrega
    UPDATE tb_delivery_envio_ARMI 
    SET 
        fecha_entrega = p_fecha_entrega,
        fecha_actualizacion = CURRENT_TIMESTAMP
    WHERE id_envio = p_id_envio;
    
    -- Verificar si se actualizó correctamente
    IF ROW_COUNT() > 0 THEN
        SET p_exito = TRUE;
        SET p_mensaje = CONCAT('Fecha de entrega actualizada correctamente para el envío ', p_id_envio);
    ELSE
        SET p_exito = FALSE;
        SET p_mensaje = CONCAT('No se pudo actualizar la fecha de entrega para el envío ', p_id_envio);
    END IF;
    
END$$

-- Procedimiento para cancelar una orden con manejo de errores
CREATE PROCEDURE sp_cancelar_orden_ARMI(
    -- Parámetros de entrada
    IN p_id_envio BIGINT,
    IN p_motivo_cancelacion VARCHAR(500),
    IN p_nota_interna TEXT,
    -- Parámetros de salida
    OUT p_exito BOOLEAN,
    OUT p_mensaje VARCHAR(500)
)
proc_cancelar: BEGIN
    -- Variables locales - deben declararse al inicio
    DECLARE v_error_code CHAR(5) DEFAULT '00000';
    DECLARE v_error_message VARCHAR(500);
    DECLARE v_existe INT DEFAULT 0;
    DECLARE v_cancelado INT DEFAULT 0;
    DECLARE v_fecha_entrega DATETIME;
    DECLARE v_fecha_creacion DATETIME;
    DECLARE v_horas_desde_creacion INT;
    
    -- Declarar handler de errores
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        GET DIAGNOSTICS CONDITION 1
            v_error_code = RETURNED_SQLSTATE,
            v_error_message = MESSAGE_TEXT;
        
        SET p_exito = FALSE;
        SET p_mensaje = CONCAT('Error SQL: ', v_error_code, ' - ', v_error_message);
    END;
    
    -- Inicializar parámetros de salida
    SET p_exito = FALSE;
    SET p_mensaje = '';
    
    -- Validaciones de entrada
    IF p_id_envio IS NULL OR p_id_envio <= 0 THEN
        SET p_mensaje = 'El ID del envío es requerido y debe ser mayor a 0';
        SET p_exito = FALSE;
        LEAVE proc_cancelar;
    END IF;
    
    IF p_motivo_cancelacion IS NULL OR TRIM(p_motivo_cancelacion) = '' THEN
        SET p_mensaje = 'El motivo de cancelación es requerido';
        SET p_exito = FALSE;
        LEAVE proc_cancelar;
    END IF;
    
    -- Limitar longitud del motivo
    IF LENGTH(p_motivo_cancelacion) > 500 THEN
        SET p_motivo_cancelacion = CONCAT(SUBSTRING(p_motivo_cancelacion, 1, 497), '...');
    END IF;
    
    -- Verificar si el envío existe y obtener su estado
    SELECT 
        COUNT(*),
        COALESCE(cancelado, 0),
        fecha_entrega,
        fecha_creacion
    INTO 
        v_existe,
        v_cancelado,
        v_fecha_entrega,
        v_fecha_creacion
    FROM tb_delivery_envio_ARMI 
    WHERE id_envio = p_id_envio;
    
    IF v_existe = 0 THEN
        SET p_mensaje = CONCAT('El envío con ID ', p_id_envio, ' no existe');
        SET p_exito = FALSE;
        LEAVE proc_cancelar;
    END IF;
    
    -- Validar estado del envío
    IF v_cancelado = 1 THEN
        SET p_mensaje = CONCAT('El envío ', p_id_envio, ' ya se encuentra cancelado');
        SET p_exito = FALSE;
        LEAVE proc_cancelar;
    END IF;
    
    IF v_fecha_entrega IS NOT NULL THEN
        SET p_mensaje = CONCAT('No se puede cancelar el envío ', p_id_envio, 
                              ' porque ya fue entregado el ', 
                              DATE_FORMAT(v_fecha_entrega, '%Y-%m-%d %H:%i:%s'));
        SET p_exito = FALSE;
        LEAVE proc_cancelar;
    END IF;
    
    -- Calcular tiempo desde creación (validación opcional)
    SET v_horas_desde_creacion = TIMESTAMPDIFF(HOUR, v_fecha_creacion, NOW());
    
    IF v_horas_desde_creacion > 24 THEN
        SET p_mensaje = CONCAT('Advertencia: El envío tiene más de 24 horas de creado (', 
                              v_horas_desde_creacion, ' horas). Confirmar cancelación.');
        -- No se bloquea, solo se advierte
    END IF;
    
    -- Actualizar estado a cancelado
    UPDATE tb_delivery_envio_ARMI 
    SET 
        cancelado = 1,
        fecha_cancelacion = CURRENT_TIMESTAMP,
        motivo_cancelacion = TRIM(p_motivo_cancelacion),
        fecha_actualizacion = CURRENT_TIMESTAMP,
        nota_interna = CASE 
            WHEN p_nota_interna IS NOT NULL AND TRIM(p_nota_interna) != '' 
            THEN CONCAT(
                COALESCE(nota_interna, ''), 
                CASE WHEN nota_interna IS NOT NULL THEN ' | ' ELSE '' END,
                '[Cancelación ', DATE_FORMAT(NOW(), '%Y-%m-%d %H:%i:%s'), ']: ',
                TRIM(p_nota_interna)
            )
            ELSE nota_interna
        END
    WHERE id_envio = p_id_envio;
    
    -- Verificar si se actualizó correctamente
    IF ROW_COUNT() > 0 THEN
        SET p_exito = TRUE;
        SET p_mensaje = CONCAT('Orden ', p_id_envio, ' cancelada correctamente');
    ELSE
        SET p_exito = FALSE;
        SET p_mensaje = CONCAT('Error inesperado al cancelar la orden ', p_id_envio);
    END IF;
    
END$$


-- Procedimiento para obtener información de un envío
CREATE PROCEDURE sp_obtener_envio_ARMI(
    -- Parámetros de entrada
    IN p_id_envio BIGINT,
    -- Parámetros de salida
    OUT p_exito BOOLEAN,
    OUT p_mensaje VARCHAR(500)
)
proc_obtener: BEGIN
    -- Variables locales - deben declararse al inicio
    DECLARE v_error_code CHAR(5) DEFAULT '00000';
    DECLARE v_error_message VARCHAR(500);
    DECLARE v_existe INT DEFAULT 0;
    
    -- Declarar handler de errores
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        GET DIAGNOSTICS CONDITION 1
            v_error_code = RETURNED_SQLSTATE,
            v_error_message = MESSAGE_TEXT;
        
        SET p_exito = FALSE;
        SET p_mensaje = CONCAT('Error SQL: ', v_error_code, ' - ', v_error_message);
    END;
    
    -- Inicializar parámetros de salida
    SET p_exito = FALSE;
    SET p_mensaje = '';
    
    -- Validaciones de entrada
    IF p_id_envio IS NULL OR p_id_envio <= 0 THEN
        SET p_mensaje = 'El ID del envío es requerido y debe ser mayor a 0';
        SET p_exito = FALSE;
        LEAVE proc_obtener;
    END IF;
    
    -- Verificar si el envío existe
    SELECT COUNT(*) INTO v_existe 
    FROM tb_delivery_envio_ARMI 
    WHERE id_envio = p_id_envio;
    
    IF v_existe = 0 THEN
        SET p_mensaje = CONCAT('El envío con ID ', p_id_envio, ' no existe');
        SET p_exito = FALSE;
        LEAVE proc_obtener;
    END IF;
    
    -- Retornar la información del envío
    SELECT 
        e.*,
        -- Información de productos
        (SELECT COUNT(*) FROM tb_delivery_productosenvio_ARMI WHERE id_envio = e.id_envio) AS total_productos,
        (SELECT SUM(quantity * unit_price) FROM tb_delivery_productosenvio_ARMI WHERE id_envio = e.id_envio) AS subtotal_productos,
        -- Estado legible
        CASE 
            WHEN e.cancelado = 1 THEN 'Cancelado'
            WHEN e.fecha_entrega IS NOT NULL THEN 'Entregado'
            ELSE 'Pendiente'
        END AS estado_legible,
        -- Método de pago legible
        CASE e.payment_method
            WHEN 1 THEN 'Efectivo'
            WHEN 2 THEN 'Datafono'
            WHEN 3 THEN 'Transferencia'
            ELSE 'Desconocido'
        END AS metodo_pago_legible,
        -- Vehículo legible
        CASE e.vehicle_type
            WHEN 1 THEN 'Bicicleta'
            WHEN 2 THEN 'Moto'
            WHEN 3 THEN 'Carro'
            ELSE 'Desconocido'
        END AS vehiculo_legible
    FROM tb_delivery_envio_ARMI e
    WHERE e.id_envio = p_id_envio;
    
    -- Retornar productos del envío
    SELECT 
        p.*,
        (p.quantity * p.unit_price) AS total_producto
    FROM tb_delivery_productosenvio_ARMI p
    WHERE p.id_envio = p_id_envio
    ORDER BY p.id_producto_envio;
    
    SET p_exito = TRUE;
    SET p_mensaje = CONCAT('Información del envío ', p_id_envio, ' obtenida correctamente');
    
END$$

DELIMITER ;


---------------------------------------------------------------------------------------------------
-- verificar scrip de maquina local casa 
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
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Tabla para registrar clientes que contratan servicios.\nUso: Quién paga/contrata el envío/pedido.\nIMPORTANTE: Puede ser TU empresa (INTEGRADOR) o un cliente final.\nEjemplo: id=1 INTEGRADOR, id=2 CLIENTE_FINAL\n';

CREATE TABLE `tb_delivery_empresa_envio` (
  `id_empresa_envio` int NOT NULL AUTO_INCREMENT,
  `nombre_empresa_envio` varchar(100) NOT NULL,
  `numero_documento` varchar(20) NOT NULL,
  `tipo_empresa` varchar(20) NOT NULL,
  `descripcion` varchar(255) DEFAULT NULL,
  `cod_estatus_empresa` int NOT NULL DEFAULT '1',
  `fecha_creacion` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `fecha_actualizacion` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_empresa_envio`),
  KEY `idx_tipo_empresa` (`tipo_empresa`),
  KEY `idx_estatus` (`cod_estatus_empresa`),
  CONSTRAINT `tb_delivery_empresa_envio_ibfk_1` FOREIGN KEY (`cod_estatus_empresa`) REFERENCES `tb_estatus_general` (`cod_estatus`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Tabla para registrar empresas de envíos (ZOOM, ARMI, otras).\nUso: Saber qué proveedor usa cada envío/pedido.\nEjemplo: id=1 ZOOM, id=2 ARMI';

CREATE TABLE `tb_delivery_envio_ARMI` (
  `id_envio` bigint NOT NULL AUTO_INCREMENT COMMENT 'ID interno único del envío',
  `business_id` bigint NOT NULL COMMENT 'ID del negocio al que pertenece la orden (BusinessId)',
  `total_value` double NOT NULL COMMENT 'Valor total de la orden (suma de productos + delivery + propinas, etc.)',
  `user_tip` double DEFAULT '0' COMMENT 'Propina opcional entregada por el usuario para el repartidor',
  `incentive_value` double DEFAULT '0' COMMENT 'Incentivo extra entregado por la empresa o plataforma',
  `delivery_value` double NOT NULL COMMENT 'Costo del servicio de entrega',
  `vehicle_type` int NOT NULL COMMENT 'Tipo de vehículo requerido (1 = bicicleta, 2 = moto, 3 = carro)',
  `payment_method` int NOT NULL COMMENT 'Método de pago (1 = efectivo, 2 = Datafono, 3 = transferencia)',
  `weight` double NOT NULL COMMENT 'Peso total de los productos (en kilogramos)',
  `city` varchar(100) NOT NULL COMMENT 'Ciudad en la que se realiza la entrega',
  `instructions` text COMMENT 'Instrucciones adicionales para el repartidor (puede estar vacío)',
  `orderInvoice` varchar(100) DEFAULT NULL COMMENT 'Código o referencia de factura de la orden (opcional o contable)',
  `token` varchar(255) DEFAULT NULL COMMENT 'Token para validar/reintentar de forma segura (puede estar vacío)',
  `first_name` varchar(100) NOT NULL COMMENT 'Nombre del cliente',
  `last_name` varchar(100) NOT NULL COMMENT 'Apellido del cliente',
  `phone` varchar(50) NOT NULL COMMENT 'Número de teléfono del cliente',
  `email` varchar(150) DEFAULT NULL COMMENT 'Dirección de correo electrónico del cliente',
  `address` text NOT NULL COMMENT 'Dirección física de entrega',
  `lat` double DEFAULT NULL COMMENT 'Latitud de la dirección de entrega',
  `lng` double DEFAULT NULL COMMENT 'Longitud de la dirección de entrega',
  `dni` varchar(50) DEFAULT NULL COMMENT 'Número de identificación del cliente (cédula, etc.)',
  `orden_status` int DEFAULT '0' COMMENT 'Estatus de la orden',
  `cancelado` tinyint(1) DEFAULT '0' COMMENT 'Indica si la orden fue cancelada (0 = no, 1 = sí)',
  `fecha_cancelacion` datetime DEFAULT NULL COMMENT 'Fecha y hora de cancelación de la orden',
  `motivo_cancelacion` varchar(500) DEFAULT NULL COMMENT 'Motivo de la cancelación',
  `fecha_creacion` datetime DEFAULT CURRENT_TIMESTAMP COMMENT 'Fecha y hora de creación del registro',
  `fecha_actualizacion` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Fecha y hora de última actualización',
  `fecha_entrega` datetime DEFAULT NULL COMMENT 'Fecha y hora de entrega del pedido',
  `nota_interna` text COMMENT 'Nota interna para comentarios administrativos',
  `instaleap_payload` json DEFAULT NULL COMMENT 'JSON recibido de la API Instaleap',
  `armi_payload` json DEFAULT NULL COMMENT 'JSON recibido de la API ARMI',
  PRIMARY KEY (`id_envio`),
  KEY `idx_business_id` (`business_id`),
  KEY `idx_city` (`city`),
  KEY `idx_fecha_creacion` (`fecha_creacion`),
  KEY `idx_payment_method` (`payment_method`),
  KEY `idx_cancelado` (`cancelado`),
  KEY `idx_fecha_entrega` (`fecha_entrega`),
  KEY `idx_token` (`token`(50))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Tabla principal de envíos de delivery';

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
) ENGINE=InnoDB AUTO_INCREMENT=23 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='La tabla tb_delivery_envio_cab_zoom almacena la información principal de los envíos generados a través del sistema de delivery, integrado con la plataforma Zoom, utilizada para logística y rastreo de paquetes.';

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
) ENGINE=InnoDB AUTO_INCREMENT=41 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='La tabla tb_delivery_envio_track_zoom almacena el historial de rastreo (tracking) de los envíos gestionados a través de Zoom.';

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

CREATE TABLE `tb_delivery_productosenvio_ARMI` (
  `id_producto_envio` bigint NOT NULL AUTO_INCREMENT COMMENT 'ID interno único del producto en el envío',
  `id_envio` bigint NOT NULL COMMENT 'ID del envío relacionado (FK a tb_delivery_envio_ARMI)',
  `product_id` bigint DEFAULT NULL COMMENT 'ID del producto en la tienda (opcional). Si es nulo, se autoincrementa por envío',
  `name` varchar(200) NOT NULL COMMENT 'Nombre del producto',
  `description` text COMMENT 'Descripción breve del producto',
  `quantity` bigint NOT NULL COMMENT 'Cantidad solicitada',
  `image_url` varchar(500) DEFAULT NULL COMMENT 'URL de imagen representativa del producto',
  `unit_price` double NOT NULL COMMENT 'Precio unitario del producto',
  `store_id` bigint NOT NULL COMMENT 'ID de la tienda donde se adquiere el producto (BranchOfficeId)',
  `fecha_creacion` datetime DEFAULT CURRENT_TIMESTAMP COMMENT 'Fecha y hora de creación del registro',
  PRIMARY KEY (`id_producto_envio`),
  KEY `idx_id_envio` (`id_envio`),
  KEY `idx_product_id` (`product_id`),
  KEY `idx_store_id` (`store_id`),
  KEY `idx_fecha_creacion` (`fecha_creacion`),
  KEY `idx_name` (`name`(100)),
  CONSTRAINT `tb_delivery_productosenvio_ARMI_ibfk_1` FOREIGN KEY (`id_envio`) REFERENCES `tb_delivery_envio_ARMI` (`id_envio`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Tabla de productos incluidos en cada envío';

CREATE TABLE `tb_delivery_tracking_ARMI` (
  `id_tracking` bigint NOT NULL AUTO_INCREMENT COMMENT 'ID interno único del registro de tracking',
  `id_envio` bigint NOT NULL COMMENT 'ID del envío relacionado (FK a tb_delivery_envio_ARMI)',
  `estado_id` int NOT NULL COMMENT 'ID numérico del estado (según catálogo interno)',
  `estado_nombre` varchar(50) NOT NULL COMMENT 'Nombre del estado (ej: ENTREGADA, CANCELADA, EN CAMINO)',
  `estado_descripcion` varchar(500) DEFAULT NULL COMMENT 'Descripción detallada del estado',
  `latitud` double DEFAULT NULL COMMENT 'Latitud de la ubicación en el momento del estado',
  `longitud` double DEFAULT NULL COMMENT 'Longitud de la ubicación en el momento del estado',
  `fecha_estado` datetime NOT NULL COMMENT 'Fecha y hora en que se produjo el estado',
  PRIMARY KEY (`id_tracking`),
  KEY `idx_id_envio` (`id_envio`),
  KEY `idx_estado_id` (`estado_id`),
  KEY `idx_estado_nombre` (`estado_nombre`),
  KEY `idx_fecha_estado` (`fecha_estado`),
  CONSTRAINT `tb_delivery_tracking_ARMI_ibfk_1` FOREIGN KEY (`id_envio`) REFERENCES `tb_delivery_envio_ARMI` (`id_envio`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Tabla de historial de tracking de estados de envíos (ARMI y otros sistemas)';

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

CREATE DEFINER=`root`@`localhost` PROCEDURE `Lysto`.`sp_actualizar_fecha_entrega_ARMI`(
    -- Parámetros de entrada
    IN p_id_envio BIGINT,
    IN p_fecha_entrega DATETIME,
    -- Parámetros de salida
    OUT p_exito BOOLEAN,
    OUT p_mensaje VARCHAR(500)
)
proc_actualizar_fecha: BEGIN
    -- Variables locales - deben declararse al inicio
    DECLARE v_error_code CHAR(5) DEFAULT '00000';
    DECLARE v_error_message VARCHAR(500);
    DECLARE v_existe INT DEFAULT 0;
    DECLARE v_cancelado INT DEFAULT 0;
    DECLARE v_ya_entregado INT DEFAULT 0;
    DECLARE v_fecha_actual DATETIME;
    
    -- Declarar handler de errores
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        GET DIAGNOSTICS CONDITION 1
            v_error_code = RETURNED_SQLSTATE,
            v_error_message = MESSAGE_TEXT;
        
        SET p_exito = FALSE;
        SET p_mensaje = CONCAT('Error SQL: ', v_error_code, ' - ', v_error_message);
    END;
    
    -- Inicializar parámetros de salida
    SET p_exito = FALSE;
    SET p_mensaje = '';
    
    -- Validaciones de entrada
    IF p_id_envio IS NULL OR p_id_envio <= 0 THEN
        SET p_mensaje = 'El ID del envío es requerido y debe ser mayor a 0';
        SET p_exito = FALSE;
        LEAVE proc_actualizar_fecha;
    END IF;
    
    IF p_fecha_entrega IS NULL THEN
        SET p_mensaje = 'La fecha de entrega es requerida';
        SET p_exito = FALSE;
        LEAVE proc_actualizar_fecha;
    END IF;
    
    -- Verificar si la fecha de entrega es futura (validación opcional)
    IF p_fecha_entrega > NOW() THEN
        SET p_mensaje = 'Advertencia: La fecha de entrega es futura';
        -- No se bloquea, solo se advierte
    END IF;
    
    -- Verificar si el envío existe y obtener su estado
    SELECT 
        COUNT(*),
        COALESCE(cancelado, 0),
        CASE WHEN fecha_entrega IS NOT NULL THEN 1 ELSE 0 END,
        fecha_entrega
    INTO 
        v_existe,
        v_cancelado,
        v_ya_entregado,
        v_fecha_actual
    FROM tb_delivery_envio_ARMI 
    WHERE id_envio = p_id_envio;
    
    IF v_existe = 0 THEN
        SET p_mensaje = CONCAT('El envío con ID ', p_id_envio, ' no existe');
        SET p_exito = FALSE;
        LEAVE proc_actualizar_fecha;
    END IF;
    
    -- Validar estado del envío
    IF v_cancelado = 1 THEN
        SET p_mensaje = CONCAT('No se puede actualizar fecha de entrega. El envío ', p_id_envio, ' está cancelado');
        SET p_exito = FALSE;
        LEAVE proc_actualizar_fecha;
    END IF;
    
    IF v_ya_entregado = 1 THEN
        -- Verificar si ya tiene la misma fecha
        IF v_fecha_actual = p_fecha_entrega THEN
            SET p_mensaje = CONCAT('El envío ', p_id_envio, ' ya tiene esta fecha de entrega');
            SET p_exito = TRUE; -- Se considera éxito porque no hay cambio
            LEAVE proc_actualizar_fecha;
        ELSE
            SET p_mensaje = CONCAT('El envío ', p_id_envio, ' ya fue entregado el ', 
                                  DATE_FORMAT(v_fecha_actual, '%Y-%m-%d %H:%i:%s'));
            SET p_exito = FALSE;
            LEAVE proc_actualizar_fecha;
        END IF;
    END IF;
    
    -- Actualizar fecha de entrega
    UPDATE tb_delivery_envio_ARMI 
    SET 
        fecha_entrega = p_fecha_entrega,
        fecha_actualizacion = CURRENT_TIMESTAMP
    WHERE id_envio = p_id_envio;
    
    -- Verificar si se actualizó correctamente
    IF ROW_COUNT() > 0 THEN
        SET p_exito = TRUE;
        SET p_mensaje = CONCAT('Fecha de entrega actualizada correctamente para el envío ', p_id_envio);
    ELSE
        SET p_exito = FALSE;
        SET p_mensaje = CONCAT('No se pudo actualizar la fecha de entrega para el envío ', p_id_envio);
    END IF;
    
END;

CREATE DEFINER=`root`@`localhost` PROCEDURE `Lysto`.`sp_actualizar_tracking_zoom`(
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

CREATE DEFINER=`root`@`localhost` PROCEDURE `Lysto`.`sp_busqueda_zoom`(
    -- Parámetros de búsqueda (todos opcionales)
    IN p_id_guia VARCHAR(100),
    /*IN p_id_cliente VARCHAR(100),
    IN p_nombre_cliente VARCHAR(200),
    IN p_tipo_cliente VARCHAR(100),
    IN p_tipo_documento VARCHAR(50),
    IN p_cod_estatus VARCHAR(50),*/
    IN p_fecha_desde DATE,
    IN p_fecha_hasta DATE 
)
BEGIN
    SELECT
        c.*,
        e.*,
        s.*
    FROM tb_delivery_cliente AS c
    LEFT JOIN tb_delivery_envio_cab_zoom AS e
        ON c.id_cliente = e.id_cliente
    LEFT JOIN tb_estatus_general AS s
        ON s.cod_estatus = e.cod_estatus_envio
    WHERE s.modulo_estatus = 'ENVIO'
        -- Búsqueda por guía (LIKE)
        AND (p_id_guia IS NULL OR p_id_guia = '' 
             OR e.id_guia_zoom LIKE CONCAT('%', p_id_guia, '%'))
        
        -- Búsqueda por ID cliente (LIKE o exacto)
        /*AND (p_id_cliente IS NULL OR p_id_cliente = '' 
             OR c.id_cliente LIKE CONCAT('%', p_id_cliente, '%'))
        
        -- Búsqueda por nombre cliente (LIKE insensible a mayúsculas)
        AND (p_nombre_cliente IS NULL OR p_nombre_cliente = '' 
             OR UPPER(c.nombre_cliente) LIKE UPPER(CONCAT('%', p_nombre_cliente, '%')))
        
        -- Búsqueda por tipo cliente (LIKE)
        AND (p_tipo_cliente IS NULL OR p_tipo_cliente = '' 
             OR UPPER(c.tipo_cliente) LIKE UPPER(CONCAT('%', p_tipo_cliente, '%')))
        
        -- Búsqueda por tipo documento (LIKE)
        AND (p_tipo_documento IS NULL OR p_tipo_documento = '' 
             OR UPPER(c.tipo_documento) LIKE UPPER(CONCAT('%', p_tipo_documento, '%')))
        
        -- Búsqueda por código de estatus
        AND (p_cod_estatus IS NULL OR p_cod_estatus = '' 
             OR e.cod_estatus_envio LIKE CONCAT('%', p_cod_estatus, '%'))*/
        
        -- Rango de fechas (creación del cliente)
        AND (p_fecha_desde IS NULL OR c.fecha_creacion >= p_fecha_desde)
        AND (p_fecha_hasta IS NULL OR c.fecha_creacion <= p_fecha_hasta)
    
    ORDER BY c.fecha_creacion DESC, e.id_guia_zoom
    LIMIT 1000; -- Límite por seguridad
    
END;

CREATE DEFINER=`root`@`localhost` PROCEDURE `Lysto`.`sp_cancelar_orden_ARMI`(
    -- Parámetros de entrada
    IN p_id_envio BIGINT,
    IN p_motivo_cancelacion VARCHAR(500),
    IN p_nota_interna TEXT,
    -- Parámetros de salida
    OUT p_exito BOOLEAN,
    OUT p_mensaje VARCHAR(500)
)
proc_cancelar: BEGIN
    -- Variables locales - deben declararse al inicio
    DECLARE v_error_code CHAR(5) DEFAULT '00000';
    DECLARE v_error_message VARCHAR(500);
    DECLARE v_existe INT DEFAULT 0;
    DECLARE v_cancelado INT DEFAULT 0;
    DECLARE v_fecha_entrega DATETIME;
    DECLARE v_fecha_creacion DATETIME;
    DECLARE v_horas_desde_creacion INT;
    
    -- Declarar handler de errores
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        GET DIAGNOSTICS CONDITION 1
            v_error_code = RETURNED_SQLSTATE,
            v_error_message = MESSAGE_TEXT;
        
        SET p_exito = FALSE;
        SET p_mensaje = CONCAT('Error SQL: ', v_error_code, ' - ', v_error_message);
    END;
    
    -- Inicializar parámetros de salida
    SET p_exito = FALSE;
    SET p_mensaje = '';
    
    -- Validaciones de entrada
    IF p_id_envio IS NULL OR p_id_envio <= 0 THEN
        SET p_mensaje = 'El ID del envío es requerido y debe ser mayor a 0';
        SET p_exito = FALSE;
        LEAVE proc_cancelar;
    END IF;
    
    IF p_motivo_cancelacion IS NULL OR TRIM(p_motivo_cancelacion) = '' THEN
        SET p_mensaje = 'El motivo de cancelación es requerido';
        SET p_exito = FALSE;
        LEAVE proc_cancelar;
    END IF;
    
    -- Limitar longitud del motivo
    IF LENGTH(p_motivo_cancelacion) > 500 THEN
        SET p_motivo_cancelacion = CONCAT(SUBSTRING(p_motivo_cancelacion, 1, 497), '...');
    END IF;
    
    -- Verificar si el envío existe y obtener su estado
    SELECT 
        COUNT(*),
        COALESCE(cancelado, 0),
        fecha_entrega,
        fecha_creacion
    INTO 
        v_existe,
        v_cancelado,
        v_fecha_entrega,
        v_fecha_creacion
    FROM tb_delivery_envio_ARMI 
    WHERE id_envio = p_id_envio;
    
    IF v_existe = 0 THEN
        SET p_mensaje = CONCAT('El envío con ID ', p_id_envio, ' no existe');
        SET p_exito = FALSE;
        LEAVE proc_cancelar;
    END IF;
    
    -- Validar estado del envío
    IF v_cancelado = 1 THEN
        SET p_mensaje = CONCAT('El envío ', p_id_envio, ' ya se encuentra cancelado');
        SET p_exito = FALSE;
        LEAVE proc_cancelar;
    END IF;
    
    IF v_fecha_entrega IS NOT NULL THEN
        SET p_mensaje = CONCAT('No se puede cancelar el envío ', p_id_envio, 
                              ' porque ya fue entregado el ', 
                              DATE_FORMAT(v_fecha_entrega, '%Y-%m-%d %H:%i:%s'));
        SET p_exito = FALSE;
        LEAVE proc_cancelar;
    END IF;
    
    -- Calcular tiempo desde creación (validación opcional)
    SET v_horas_desde_creacion = TIMESTAMPDIFF(HOUR, v_fecha_creacion, NOW());
    
    IF v_horas_desde_creacion > 24 THEN
        SET p_mensaje = CONCAT('Advertencia: El envío tiene más de 24 horas de creado (', 
                              v_horas_desde_creacion, ' horas). Confirmar cancelación.');
        -- No se bloquea, solo se advierte
    END IF;
    
    -- Actualizar estado a cancelado
    UPDATE tb_delivery_envio_ARMI 
    SET 
        cancelado = 1,
        fecha_cancelacion = CURRENT_TIMESTAMP,
        motivo_cancelacion = TRIM(p_motivo_cancelacion),
        fecha_actualizacion = CURRENT_TIMESTAMP,
        nota_interna = CASE 
            WHEN p_nota_interna IS NOT NULL AND TRIM(p_nota_interna) != '' 
            THEN CONCAT(
                COALESCE(nota_interna, ''), 
                CASE WHEN nota_interna IS NOT NULL THEN ' | ' ELSE '' END,
                '[Cancelación ', DATE_FORMAT(NOW(), '%Y-%m-%d %H:%i:%s'), ']: ',
                TRIM(p_nota_interna)
            )
            ELSE nota_interna
        END
    WHERE id_envio = p_id_envio;
    
    -- Verificar si se actualizó correctamente
    IF ROW_COUNT() > 0 THEN
        SET p_exito = TRUE;
        SET p_mensaje = CONCAT('Orden ', p_id_envio, ' cancelada correctamente');
    ELSE
        SET p_exito = FALSE;
        SET p_mensaje = CONCAT('Error inesperado al cancelar la orden ', p_id_envio);
    END IF;
    
END;

CREATE DEFINER=`root`@`localhost` PROCEDURE `Lysto`.`sp_crear_envio_zoom`(
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
  -- IN p_payload_track JSON,
  
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
        fecha_creacion,
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
        JSON_OBJECT('mensaje', 'Envío creado OK', 'fecha', NOW())
        -- IFNULL(p_payload_track, JSON_OBJECT('source', 'sp_crear_envio_zoom'))
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

CREATE DEFINER=`root`@`localhost` PROCEDURE `Lysto`.`sp_guardar_envio_ARMI`(
    -- Parámetros de entrada
    IN p_business_id BIGINT,
    IN p_total_value DOUBLE,
    IN p_user_tip DOUBLE,
    IN p_incentive_value DOUBLE,
    IN p_delivery_value DOUBLE,
    IN p_vehicle_type INT,
    IN p_payment_method INT,
    IN p_weight DOUBLE,
    IN p_city VARCHAR(100),
    IN p_instructions TEXT,
    IN p_orderInvoice VARCHAR(100),
    IN p_token VARCHAR(255),
    IN p_first_name VARCHAR(100),
    IN p_last_name VARCHAR(100),
    IN p_phone VARCHAR(50),
    IN p_email VARCHAR(150),
    IN p_address TEXT,
    IN p_lat DOUBLE,
    IN p_lng DOUBLE,
    IN p_dni VARCHAR(50),
    IN p_nota_interna TEXT,
    IN p_instaleap_payload JSON,
    IN p_armi_payload JSON,
    -- Parámetros de salida
    OUT p_exito BOOLEAN,
    OUT p_mensaje VARCHAR(500),
    OUT p_id_envio_generado BIGINT
)
proc_insertar: BEGIN
    -- Variables locales - deben declararse al inicio
    DECLARE v_error_code CHAR(5) DEFAULT '00000';
    DECLARE v_error_message VARCHAR(500);
    DECLARE v_existing_token INT DEFAULT 0;
    DECLARE v_max_retries INT DEFAULT 3;
    DECLARE v_retry_count INT DEFAULT 0;
    DECLARE v_success BOOLEAN DEFAULT FALSE;
    -- DECLARE v_duplicate_entry BOOLEAN DEFAULT FALSE; -- Nueva variable para controlar duplicados
    
    -- Declarar handler principal de errores
    /*DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        GET DIAGNOSTICS CONDITION 1
            v_error_code = RETURNED_SQLSTATE,
            v_error_message = MESSAGE_TEXT;
        
        SET p_exito = FALSE;
        SET p_mensaje = CONCAT('Error SQL: ', v_error_code, ' - ', v_error_message);
        
        -- Log del error (opcional)
        -- INSERT INTO tabla_log_errores (procedimiento, error_code, error_message, fecha) 
        -- VALUES ('sp_insertar_envio_completo_ARMI', v_error_code, v_error_message, NOW());
    END;*/
    
    -- Inicializar parámetros de salida
    SET p_exito = FALSE;
    SET p_mensaje = '';
    SET p_id_envio_generado = NULL;
    
    -- Validaciones de entrada
    IF p_business_id IS NULL OR p_business_id <= 0 THEN
        SET p_mensaje = 'El business_id es requerido y debe ser mayor a 0';
        SET p_exito = FALSE;
        LEAVE proc_insertar;
    END IF;
    
    IF p_total_value IS NULL OR p_total_value < 0 THEN
        SET p_mensaje = 'El total_value es requerido y no puede ser negativo';
        SET p_exito = FALSE;
        LEAVE proc_insertar;
    END IF;
    
    IF p_delivery_value IS NULL OR p_delivery_value < 0 THEN
        SET p_mensaje = 'El delivery_value es requerido y no puede ser negativo';
        SET p_exito = FALSE;
        LEAVE proc_insertar;
    END IF;
    
    IF p_vehicle_type NOT IN (1, 2, 3) THEN
        SET p_mensaje = 'El vehicle_type debe ser 1 (bicicleta), 2 (moto) o 3 (carro)';
        SET p_exito = FALSE;
        LEAVE proc_insertar;
    END IF;
    
    IF p_payment_method NOT IN (1, 2, 3) THEN
        SET p_mensaje = 'El payment_method debe ser 1 (efectivo), 2 (Datafono) o 3 (transferencia)';
        SET p_exito = FALSE;
        LEAVE proc_insertar;
    END IF;
    
    IF p_city IS NULL OR TRIM(p_city) = '' THEN
        SET p_mensaje = 'La ciudad es requerida';
        SET p_exito = FALSE;
        LEAVE proc_insertar;
    END IF;
    
    IF p_first_name IS NULL OR TRIM(p_first_name) = '' THEN
        SET p_mensaje = 'El nombre del cliente es requerido';
        SET p_exito = FALSE;
        LEAVE proc_insertar;
    END IF;
    
    IF p_phone IS NULL OR TRIM(p_phone) = '' THEN
        SET p_mensaje = 'El teléfono del cliente es requerido';
        SET p_exito = FALSE;
        LEAVE proc_insertar;
    END IF;
    
    IF p_address IS NULL OR TRIM(p_address) = '' THEN
        SET p_mensaje = 'La dirección de entrega es requerida';
        SET p_exito = FALSE;
        LEAVE proc_insertar;
    END IF;
    
    -- Validar token único si se proporciona
    IF p_token IS NOT NULL AND TRIM(p_token) != '' THEN
        SELECT COUNT(*) INTO v_existing_token 
        FROM tb_delivery_envio_ARMI 
        WHERE token = p_token;
        
        IF v_existing_token > 0 THEN
            SET p_mensaje = CONCAT('El token ya existe en el sistema: ', p_token);
            SET p_exito = FALSE;
            LEAVE proc_insertar;
        END IF;
    END IF;
    
    -- Validar JSON payloads
    IF p_instaleap_payload IS NOT NULL AND NOT JSON_VALID(p_instaleap_payload) THEN
        SET p_mensaje = 'El payload de Instaleap no es un JSON válido';
        SET p_exito = FALSE;
        LEAVE proc_insertar;
    END IF;
    
    IF p_armi_payload IS NOT NULL AND NOT JSON_VALID(p_armi_payload) THEN
        SET p_mensaje = 'El payload de ARMI no es un JSON válido';
        SET p_exito = FALSE;
        LEAVE proc_insertar;
    END IF;
    
    -- Intentar inserción con reintentos
    SET v_retry_count = 0;
    SET v_success = FALSE;
    if p_mensaje = '' then
    	SET v_success = FALSE;
    	SET p_mensaje = 'ERROR desconocido antes de insertar registros';
    else
    /*WHILE v_retry_count < v_max_retries AND NOT v_success DO
        BEGIN*/
            -- Handler específico para error 1062 (duplicado)
            /*DECLARE CONTINUE HANDLER FOR 1062 
            BEGIN
                SET v_duplicate_entry = TRUE;
            END;
            
            DECLARE CONTINUE HANDLER FOR SQLEXCEPTION 
            BEGIN
                SET v_error_message = 'Error durante la inserción';
            END;*/
            
            -- Resetear la variable de duplicado
            -- SET v_duplicate_entry = FALSE;
            
            -- Insertar en la tabla principal
            INSERT INTO tb_delivery_envio_ARMI (
                business_id, total_value, user_tip, incentive_value, 
                delivery_value, vehicle_type, payment_method, weight, 
                city, instructions, orderInvoice, token, first_name, 
                last_name, phone, email, address, lat, lng, dni,
                nota_interna, instaleap_payload, armi_payload
            ) VALUES (
                p_business_id, p_total_value, 
                COALESCE(p_user_tip, 0.00), 
                COALESCE(p_incentive_value, 0.00),
                p_delivery_value, p_vehicle_type, p_payment_method, 
                COALESCE(p_weight, 0.00),
                TRIM(p_city), p_instructions, p_orderInvoice, p_token, 
                TRIM(p_first_name), TRIM(p_last_name), TRIM(p_phone), 
                p_email, TRIM(p_address), p_lat, p_lng, p_dni,
                p_nota_interna, p_instaleap_payload, p_armi_payload
            );
            
            -- Si llegamos aquí sin error, éxito
            -- IF NOT v_duplicate_entry THEN
                -- Obtener el ID del envío insertado
                SET p_id_envio_generado = LAST_INSERT_ID();
                SET v_success = TRUE;
            -- ELSE
                -- Incrementar contador de reintentos
                -- SET v_retry_count = v_retry_count + 1;
                
                -- Esperar breve tiempo antes de reintentar (opcional)
                -- DO SLEEP(0.1);
            -- END IF;
        /*END;
    END WHILE;*/
     end if;
    -- Verificar éxito de la operación
    IF v_success THEN
        SET p_exito = TRUE;
        SET p_mensaje = CONCAT('Envío creado exitosamente con ID: ', p_id_envio_generado);
    /*ELSEIF v_duplicate_entry THEN
        SET p_exito = FALSE;
        SET p_mensaje = CONCAT('Error de duplicado después de ', v_max_retries, ' intentos. Token: ', p_token);*/
    ELSE
        SET p_exito = FALSE;
        -- SET p_mensaje = CONCAT('Error desconocido al crear el envío después de ', v_retry_count, ' intentos');
    END IF;
    
END;

CREATE DEFINER=`root`@`localhost` PROCEDURE `Lysto`.`sp_guarda_cliente_zoom`(
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

CREATE DEFINER=`root`@`localhost` PROCEDURE `Lysto`.`sp_obtener_envio_ARMI`(
    -- Parámetros de entrada
    IN p_id_envio BIGINT,
    -- Parámetros de salida
    OUT p_exito BOOLEAN,
    OUT p_mensaje VARCHAR(500)
)
proc_obtener: BEGIN
    -- Variables locales - deben declararse al inicio
    DECLARE v_error_code CHAR(5) DEFAULT '00000';
    DECLARE v_error_message VARCHAR(500);
    DECLARE v_existe INT DEFAULT 0;
    
    -- Declarar handler de errores
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        GET DIAGNOSTICS CONDITION 1
            v_error_code = RETURNED_SQLSTATE,
            v_error_message = MESSAGE_TEXT;
        
        SET p_exito = FALSE;
        SET p_mensaje = CONCAT('Error SQL: ', v_error_code, ' - ', v_error_message);
    END;
    
    -- Inicializar parámetros de salida
    SET p_exito = FALSE;
    SET p_mensaje = '';
    
    -- Validaciones de entrada
    IF p_id_envio IS NULL OR p_id_envio <= 0 THEN
        SET p_mensaje = 'El ID del envío es requerido y debe ser mayor a 0';
        SET p_exito = FALSE;
        LEAVE proc_obtener;
    END IF;
    
    -- Verificar si el envío existe
    SELECT COUNT(*) INTO v_existe 
    FROM tb_delivery_envio_ARMI 
    WHERE id_envio = p_id_envio;
    
    IF v_existe = 0 THEN
        SET p_mensaje = CONCAT('El envío con ID ', p_id_envio, ' no existe');
        SET p_exito = FALSE;
        LEAVE proc_obtener;
    END IF;
    
    -- Retornar la información del envío
    SELECT 
        e.*,
        -- Información de productos
        (SELECT COUNT(*) FROM tb_delivery_productosenvio_ARMI WHERE id_envio = e.id_envio) AS total_productos,
        (SELECT SUM(quantity * unit_price) FROM tb_delivery_productosenvio_ARMI WHERE id_envio = e.id_envio) AS subtotal_productos,
        -- Estado legible
        CASE 
            WHEN e.cancelado = 1 THEN 'Cancelado'
            WHEN e.fecha_entrega IS NOT NULL THEN 'Entregado'
            ELSE 'Pendiente'
        END AS estado_legible,
        -- Método de pago legible
        CASE e.payment_method
            WHEN 1 THEN 'Efectivo'
            WHEN 2 THEN 'Datafono'
            WHEN 3 THEN 'Transferencia'
            ELSE 'Desconocido'
        END AS metodo_pago_legible,
        -- Vehículo legible
        CASE e.vehicle_type
            WHEN 1 THEN 'Bicicleta'
            WHEN 2 THEN 'Moto'
            WHEN 3 THEN 'Carro'
            ELSE 'Desconocido'
        END AS vehiculo_legible
    FROM tb_delivery_envio_ARMI e
    WHERE e.id_envio = p_id_envio;
    
    -- Retornar productos del envío
    SELECT 
        p.*,
        (p.quantity * p.unit_price) AS total_producto
    FROM tb_delivery_productosenvio_ARMI p
    WHERE p.id_envio = p_id_envio
    ORDER BY p.id_producto_envio;
    
    SET p_exito = TRUE;
    SET p_mensaje = CONCAT('Información del envío ', p_id_envio, ' obtenida correctamente');
    
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