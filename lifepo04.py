# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import struct
from battery import Protection, Battery, Cell
from util_max17853 import data_cycle
from utils import *
from struct import *

# Você deve começar fazendo uma cópia do Battery_template.py e nomeando-o para o seu BMS.
# O modelo é um pequeno exemplo de implementação. Em teoria, este é o único arquivo que
# você precisará editar para adicionar seu BMS, exceto ao adicionar este novo arquivo como
# referência ao programa principalS.
# Para começar você só precisa do número de células, o soc, corrente e voltagem. Depois de 
# ler isso, o driver já deve estar 
# funcionando

class LifePo4(Battery):

    def __init__(self, port,baud):
        super(LifePo4, self).__init__(port,baud)
        self.type = self.BATTERYTYPE

# LENGTH_POS será a posição do byte do seu campo Byte Cound e LENGTH_CHECK é quantos bytes
# tem todas as coisas fora do pacote de dados.

    logger.warning('Testing Hello word PTI')
    BATTERYTYPE = "LifePo4"
    LENGTH_CHECK = 4
    LENGTH_POS = 3

    # Frame de leitura
    # ID    Funçao  endereço(hi)  Endereço(low)  Reg(hi)   Reg(lo) CRC(low) CRC(High)
    # 0x01  0x03    0x00          0x00           0x00       0xFF
    command_address = b"\x01"
    command_status = b"\x03\x00\x69\x00\x17\xD5\xD8"
    command_general = b"\x03\x00\x00\x00\x27\x05\xD0"

# Renomeie a classe BatteryTemplate para seu BMS e então você precisa usar as 3 funções
# principais que são implementadas para ler e preencher dados para seu BMS.
# (test_connection, get_settings & refresh_data)
# Essas funções são chamadas em momentos diferentes.

    def test_connection(self):

# Essa função está relacionado a função read_serial_data_lifepo4 ((crc, start bytes, etc)

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
        self.max_battery_voltage = MAX_CELL_VOLTAGE * self.cell_count
        self.min_battery_voltage = MIN_CELL_VOLTAGE * self.cell_count
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

        voltage, current, cell_voltage1, cell_voltage2, cell_voltage3, cell_voltage4, \
        cell_voltage5, cell_voltage6, cell_voltage7, cell_voltage8, cell_voltage9, \
        cell_voltage10, cell_voltage11, cell_voltage12, cell_voltage13, cell_voltage14, \
        cell_voltage15, cell_voltage16, temp_resfriamento, temp_interna, temp_max, \
        capacidade_remanescente, corrente_max_recarga, soh_bat, soc_bat, status_bat, \
        nsei1, nsei2, nsei3, nsei4, nsei5, nsei6, nsei7, nsei8, nsei9, nsei10, numero_cell, \
        nsei11, nsei12  = unpack_from('>HhHH', all_data)
            
        # unpack_from os bytes HhHH são as tensões, corrente, etc.
        self.voltage = voltage / 100
        self.current = current / 100
        # são 16 celulas 2 bytes por célula 32 byte
        #self.cell_voltage1 = cell_voltage1 / 100
        #self.cell_voltage2 = cell_voltage2 / 100
        #self.cell_voltage3 = cell_voltage3 / 100
        #self.cell_voltage4 = cell_voltage4 / 100
        #self.cell_voltage5 = cell_voltage5 / 100
        #self.cell_voltage6 = cell_voltage6 / 100
        #self.cell_voltage7 = cell_voltage7 / 100
        #self.cell_voltage8 = cell_voltage8 / 100
        #self.cell_voltage9 = cell_voltage9 / 100
        #self.cell_voltage10 = cell_voltage10 / 100
        #self.cell_voltage11 = cell_voltage11 / 100
        #self.cell_voltage12 = cell_voltage12 / 100
        #self.cell_voltage13 = cell_voltage13 / 100
        #self.cell_voltage14 = cell_voltage14 / 100
        #self.cell_voltage15 = cell_voltage15 / 100
        #self.cell_voltage16 = cell_voltage16 / 100
        #Temperatura de resfriamento do BMS
        #self.temp_resfriamento = temp_resfriamento
        #Temperatura interna da bateria
        #self.temp_interna = temp_interna
        #Temperatura máxima da célula
        #self.temp_max = temp_max
        #Capacidade remanescente da bateria
        #self.capacidade_remanescente = capacidade_remanescente
        #Corrente maxima de recarga
        #self.corrente_max_recarga = corrente_max_recarga
        #SOH
        #self.soh_bat = soh_bat
        #SOC
        self.soc_bat = soc_bat
        #Status da bateria
        #self.status_bat = status_bat
        #Registradores desconhecidos
        #self.nsei1 = nsei1
        #self.nsei2 = nsei2
        #self.nsei3 = nsei3
        #self.nsei4 = nsei4
        #self.nsei5 = nsei5
        #self.nsei6 = nsei6
        #self.nsei7 = nsei7
        #self.nsei8 = nsei8
        #self.nsei9 = nsei9
        #self.nsei10 = nsei10
        #self.nsei11 = nsei11
        #self.nsei12 = nsei12
        #Número de células
        self.numero_cell = numero_cell


        return True

#Há uma função auxiliar no bottem que você pode usar para escrever os comandos e ler seus
# dados. Existem pequenas diferenças em cada protocolo de comunicação e é aqui que os
# parâmetros para read_serial_data precisam ser ajustados para o seu BMS.


#Calculo do CRC 
#https://stackoverflow.com/questions/53358646/how-to-calculate-this-crc-using-python
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
        return struct.pack('<H',crc)

    def generate_command(self, command):
        buffer = bytearray(self.command_address)
        buffer += self.command_general

        return buffer

# use a função read_serial_data() para ler a data do BMS (crc, start bytes, etc)
    def read_serial_data_lifepo4(self, command):
        data = read_serial_data(self.generate_command(command), self.port, self.baud_rate, self.LENGTH_POS, self.LENGTH_CHECK)
        if data is False:
            return False

        id, funcao, length = unpack_from("BBB", data)
        comprimento = (length/2)

        if funcao == 3: 
            return data [4:length]
        else:
            logger.error(">>> ERRO: incorreto >>> PTI")  
#Mensagem recebida (ID)(funcao)(2*comprimeto ou length)(data)(CRC)

# O MODBUS trabalha com data frames que é um conjunto de bytes que está estruturado
# de forma a transferir os dados. Cada quadro tem um indicador de início e fim e
# para o JKBMS o início é de 2 bytes (em hexadecimal 4E e 57) e o final é de 1 byte
# (em hexadecimal 68). Portanto, este pedaço de código está verificando se recebemos
# uma resposta válida do JKBMS. Isso, juntamente com o CRC, nos mostrará que foram
# recebidos dados válidos que podemos usar.

# return data[4:length + 4] é usado para fatiar a data, pegar somente os dados que quiser
# https://pt.stackoverflow.com/questions/110054/como-funciona-a-atribui%C3%A7%C3%A3o-de-lista-usando-intervalo/110256#110256

