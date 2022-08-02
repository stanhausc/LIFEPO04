# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import struct
from battery import Protection, Battery, Cell
from util_max17853 import data_cycle
from utils import *
from struct import *


# VocÃª deve comeÃ§ar fazendo uma cÃ³pia do Battery_template.py e nomeando-o para o seu BMS.
# O modelo Ã© um pequeno exemplo de implementaÃ§Ã£o. Em teoria, este Ã© o Ãºnico arquivo que
# vocÃª precisarÃ¡ editar para adicionar seu BMS, exceto ao adicionar este novo arquivo como
# referÃªncia ao programa principalS.
# Para comeÃ§ar vocÃª sÃ³ precisa do nÃºmero de cÃ©lulas, o soc, corrente e voltagem. Depois de
# ler isso, o driver jÃ¡ deve estar
# funcionando

class LifePo4(Battery):

    def __init__(self, port, baud):
        super(LifePo4, self).__init__(port, baud)
        self.type = self.BATTERYTYPE

    # LENGTH_POS serÃ¡ a posiÃ§Ã£o do byte do seu campo Byte Cound e LENGTH_CHECK Ã© quantos bytes
    # tem todas as coisas fora do pacote de dados.

    logger.warning('Testing Hello word PTI')
    BATTERYTYPE = "UNICOBA"
    LENGTH_CHECK = 4
    LENGTH_POS = 3
    length_div = 39

    # Frame de leitura
    # ID    FunÃ§ao  endereÃ§o(hi)  EndereÃ§o(low)  Reg(hi)   Reg(lo) CRC(low) CRC(High)
    # 0x01  0x03    0x00          0x00           0x00       0xFF
    command_address = b"\x01"
    command_status = b"\x03\x00\x69\x00\x17\xD5\xD8"
    command_general = b"\x01\x03\x00\x00\x00\x27\x05\xD0"

    # Renomeie a classe BatteryTemplate para seu BMS e entÃ£o vocÃª precisa usar as 3 funÃ§Ãµes
    # principais que sÃ£o implementadas para ler e preencher dados para seu BMS.
    # (test_connection, get_settings & refresh_data)
    # Essas funÃ§Ãµes sÃ£o chamadas em momentos diferentes.

    def test_connection(self):

        # Essa funÃ§Ã£o estÃ¡ relacionado a funÃ§Ã£o read_serial_data_lifepo4 ((crc, start bytes, etc)

        # call a function that will connect to the battery, send a command and retrieve the result.
        # The result or call should be unique to this BMS. Battery name or version, etc.
        # Return True if success, False for failure
        return self.read_all_data()

    def get_settings(self):
        # After successful  connection get_settings will be call to set up the battery.
        # Set the current limits, populate cell count, etc
        # Return True if success, False for failure
        self.max_battery_current = MAX_BATTERY_CURRENT
        self.max_battery_discharge_current = MAX_BATTERY_DISCHARGE_CURRENT
        self.max_battery_voltage = MAX_CELL_VOLTAGE * self.numero_cell
        self.min_battery_voltage = MIN_CELL_VOLTAGE * self.numero_cell
        return True

    def refresh_data(self):
        # call all functions that will refresh the battery data.
        # This will be called for every iteration (1 second)
        # Return True if success, False for failure
        result = self.read_all_data()
        result = result and self.read_all_data
        return result

    def read_all_data(self):
        all_data = self.read_serial_data_lifepo4(self.command_general)
        if all_data is False:
            return False
        # 42 registradores
        id, funcao, length, tensao, corrente, cell_voltage1, cell_voltage2, cell_voltage3, cell_voltage4, cell_voltage5, cell_voltage6,\
        cell_voltage7, cell_voltage8, cell_voltage9, cell_voltage10, cell_voltage11, cell_voltage12, cell_voltage13, cell_voltage14,\
        cell_voltage15, cell_voltage16, temp_resfriamento, temp_interna, temp_max, capacidade_remanescente, corrente_max, soh_bat, soc_bat, status_bat,\
        nsei1, nsei2, nsei3, nsei4, nsei5, nsei6, nsei7, nsei8, nsei9, nsei10, numero_cell, nsei11, nsei12 = unpack_from(">BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB", all_data)

        self.id = id
        self.funcao = funcao
        self.length = length
        # unpack_from os bytes HhHH sÃ£o as tensÃµes, corrente, etc.
        self.voltage = tensao / 100
        self.current = corrente / 100
        # sÃ£o 16 celulas 2 bytes por cÃ©lula 32 byte
        self.cell_voltage1 = cell_voltage1 / 100
        self.cell_voltage2 = cell_voltage2 / 100
        self.cell_voltage3 = cell_voltage3 / 100
        self.cell_voltage4 = cell_voltage4 / 100
        self.cell_voltage5 = cell_voltage5 / 100
        self.cell_voltage6 = cell_voltage6 / 100
        self.cell_voltage7 = cell_voltage7 / 100
        self.cell_voltage8 = cell_voltage8 / 100
        self.cell_voltage9 = cell_voltage9 / 100
        self.cell_voltage10 = cell_voltage10 / 100
        self.cell_voltage11 = cell_voltage11 / 100
        self.cell_voltage12 = cell_voltage12 / 100
        self.cell_voltage13 = cell_voltage13 / 100
        self.cell_voltage14 = cell_voltage14 / 100
        self.cell_voltage15 = cell_voltage15 / 100
        self.cell_voltage16 = cell_voltage16 / 100
        # Temperatura de resfriamento do BMS
        self.temp_resfriamento = temp_resfriamento
        # Temperatura interna da bateria
        self.temp_interna = temp_interna
        # Temperatura mÃ¡xima da cÃ©lula
        self.temp_max = temp_max
        # Capacidade remanescente da bateria
        self.capacidade_remanescente = capacidade_remanescente
        # Corrente maxima de recarga
        self.corrente_max = corrente_max
        # SOH
        self.soh_bat = soh_bat
        # SOC
        self.soc_bat = soc_bat
        # Status da bateria
        self.status_bat = status_bat
        # Registradores desconhecidos
        self.nsei1 = nsei1
        self.nsei2 = nsei2
        self.nsei3 = nsei3
        self.nsei4 = nsei4
        self.nsei5 = nsei5
        self.nsei6 = nsei6
        self.nsei7 = nsei7
        self.nsei8 = nsei8
        self.nsei9 = nsei9
        self.nsei10 = nsei10
        self.nsei11 = nsei11
        self.nsei12 = nsei12
        # NÃºmero de cÃ©lulas
        self.numero_cell = numero_cell
        print("estamos na read all data")
        print(soc_bat)

        return True

    # HÃ¡ uma funÃ§Ã£o auxiliar no bottem que vocÃª pode usar para escrever os comandos e ler seus
    # dados. Existem pequenas diferenÃ§as em cada protocolo de comunicaÃ§Ã£o e Ã© aqui que os
    # parÃ¢metros para read_serial_data precisam ser ajustados para o seu BMS.

    # Calculo do CRC
    # https://stackoverflow.com/questions/53358646/how-to-calculate-this-crc-using-python
    def crc_16_CCITT(self, data):
        crc = 0xFFFF

        for pos in data:
            crc ^= pos
            for i in range(8):
                if ((crc & 1) != 0):
                    crc >>= 1
                    crc ^= 0xA001
                else:
                    crc >>= 1
        return struct.pack('<H', crc)

    def generate_command(self, command):
        buffer = bytearray(self.command_general)

        return buffer

    # use a funÃ§Ã£o read_serial_data() para ler a data do BMS (crc, start bytes, etc)
    def read_serial_data_lifepo4(self, command):
        data = read_serial_data(self.generate_command(command), self.port, self.baud_rate, self.LENGTH_POS, self.LENGTH_CHECK, self.length_div)
        if data is False:
            return False

        id, funcao, length = unpack_from("BBB", data)

        if funcao == 3:
            print(id)
            print(funcao)
            print(length)
            print(data[3:length+3])
            print(data)
            print(command)
            print(command[2:7])
            print(self.length_div)
            return data[: self.length_div+3]
        else:
            logger.error(">>> ERRO: incorreto >>> PTI")
        # Mensagem recebida (ID)(funcao)(2*comprimeto ou length)(data)(CRC)

# O MODBUS trabalha com data frames que Ã© um conjunto de bytes que estÃ¡ estruturado
# de forma a transferir os dados. Cada quadro tem um indicador de inÃ­cio e fim e
# para o JKBMS o inÃ­cio Ã© de 2 bytes (em hexadecimal 4E e 57) e o final Ã© de 1 byte
# (em hexadecimal 68). Portanto, este pedaÃ§o de cÃ³digo estÃ¡ verificando se recebemos
# uma resposta vÃ¡lida do JKBMS. Isso, juntamente com o CRC, nos mostrarÃ¡ que foram
# recebidos dados vÃ¡lidos que podemos usar.

# return data[4:length + 4] Ã© usado para fatiar a data, pegar somente os dados que quiser
# https://pt.stackoverflow.com/questions/110054/como-funciona-a-atribui%C3%A7%C3%A3o-de-lista-usando-intervalo/110256#110256

