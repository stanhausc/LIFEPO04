# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from asyncio import sleep
from asyncio.log import logger
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

    def __init__(self, port, baud):
        super(LifePo4, self).__init__(port, baud)
        self.type = self.BATTERYTYPE

    # LENGTH_POS será a posição do byte do seu campo Byte Cound e LENGTH_CHECK é quantos bytes
    # tem todas as coisas fora do pacote de dados.

    logger.warning('Testing Hello word PTI')
    BATTERYTYPE = "UNICOBA"
    LENGTH_CHECK = 4
    LENGTH_POS = 3

    # Frame de leitura
    # ID    Funçao  endereço(hi)  Endereço(low)  Reg(hi)   Reg(lo) CRC(low) CRC(High)
    # 0x01  0x03    0x00          0x00           0x00       0xFF
    command_geral = b"\x01\x03\x00\x00\x00\x27\x05\xD0"
    command_numero_cell = b'\x01\x03\x00\x24\x00\x01\xC4\x01'
    command_soc = b"\x01\x03\x00\x18\x00\x01\x04\x0D"
    command_tensao_cell = b'\x01\x03\x00\x02\x00\x10\xE5\xC6'
    command_temp = b"\x01\x03\x00\x12\x00\x03\xA5\xCE"

    

    # Renomeie a classe BatteryTemplate para seu BMS e então você precisa usar as 3 funções
    # principais que são implementadas para ler e preencher dados para seu BMS.
    # (test_connection, get_settings & refresh_data)
    # Essas funções são chamadas em momentos diferentes.

    def test_connection(self):

        # Essa função está relacionado a função read_serial_data_lifepo4 ((crc, start bytes, etc)

        # call a function that will connect to the battery, send a command and retrieve the result.
        # The result or call should be unique to this BMS. Battery name or version, etc.
        # Return True if success, False for failure
        return self.read_soc()

    def get_settings(self):
        # After successful  connection get_settings will be call to set up the battery.
        # Set the current limits, populate cell count, etc
        # Return True if success, False for failure

        self.max_battery_current = MAX_BATTERY_CURRENT
        self.max_battery_discharge_current = MAX_BATTERY_DISCHARGE_CURRENT

        if self.cell_count is None:
          self.read_numero_cell()
        self.max_battery_voltage = MAX_CELL_VOLTAGE * self.cell_count
        self.min_battery_voltage = MIN_CELL_VOLTAGE * self.cell_count

        return True

    def refresh_data(self):
        # call all functions that will refresh the battery data.
        # This will be called for every iteration (1 second)
        # Return True if success, False for failure
        result = self.read_soc()
        result = result and self.read_all_data()
        result = result and self.read_temp()
        result = result and self.read_cell_data()
       
        return result

    def read_temp(self):
        data_temp = self.read_serial_data_lifepo4(self.command_temp)
        if data_temp is None:
            logger.warning("PTI_erro_ao_Ler_temperaturas")
            return False

        id, funcao, length, temp_resfriamento, temp_interna, temp_max = unpack_from(">BBBhhh", data_temp)

        self.id = id
        self.funcao = funcao
        self.length = length
        # Temperatura de resfriamento do BMS
        self.temp_resfriamento = temp_resfriamento
        # Temperatura interna da bateria
        self.temp1 = temp_interna
        # Temperatura máxima da célula
        self.temp2 = temp_max

        print(" >>> Estamos em read_temp")
        print("############# Temperatura resfriamento BMS =", temp_resfriamento, '°C' )
        print("############# Temperatura interna da bateria =", temp_interna, '°C' )
        print("############# Temperatura máxima da célula =", temp_max, '°C' )
        return True

    def read_cell_data(self):
        cell_data = self.read_serial_data_lifepo4(self.command_tensao_cell)
        # check if connect success
        if cell_data is None:
            logger.warning("PTI_erro_ao_Ler_tensão_de_celulas")
            return False

        for c in range(self.cell_count):
            try:
                id, funcao, length, cell_volts = unpack_from('>BBBH', cell_data, c * 2)
                if len(cell_volts) != 0:
                    self.cells[c].voltage = cell_volts[0] / 1000
            except struct.error:
                self.cells[c].voltage = 0
        return True    

    def read_numero_cell(self):
        data_cell = self.read_serial_data_lifepo4(self.command_numero_cell)
        if data_cell is None:
            logger.warning("PTI_erro_ao_Ler_Numero_de_celulas")
            return False

        id, funcao, length, cell_count = unpack_from(">BBBH", data_cell)

        self.id = id
        self.funcao = funcao
        self.length = length
        self.cell_count = cell_count
        print(" >>> Estamos em read_numero_cell")
        print ("############# numero de celulas =", cell_count)
        return True

    def read_all_data(self):
        all_data = self.read_serial_data_lifepo4(self.command_geral)
        if all_data is None:
            logger.warning("PTI_erro_ao_Ler_Tensoes")
            return False
        # 42 registradores (com id funcao e length)
        id, funcao, length, tensao, corrente = unpack_from(">BBBHh", all_data)

        self.id = id
        self.funcao = funcao
        self.length = length
        # unpack_from os bytes HhHH são as tensões, corrente, etc.
        self.voltage = tensao / 100
        self.current = corrente / 100

        print(' >>>>> Estamos em read all_data')
        print('id', id)
        print("funcao", funcao)
        print("length", length)
        print('############# tensao', tensao/100, "V")
        print('############# corrente = ', corrente, 'A')

        return True

    def read_soc(self):
        data_soc = self.read_serial_data_lifepo4(self.command_soc)
        if data_soc is False or len(data_soc) < 5:
            logger.warning("PTI_erro_ao_Ler_SOC")
            return False
        
        id, funcao, length, soc = unpack_from(">BBBH", data_soc)

        self.id = id
        self.funcao = funcao
        self.length = length
        self.soc = soc
        print(" >>> Estamos em read_soc")
        print ("############# soc =", soc, "%")

        return True


    def read_serial_data_lifepo4(self, command):
        data = read_serial_data(command, self.port, self.baud_rate, self.LENGTH_POS, self.LENGTH_CHECK)
        if data is False:
            return False

        id, funcao, length = unpack_from(">BBB", data)

        if funcao == 3:
            print(" >>> Estamos em read_serial_data")
            print('id', id)
            print("funcao", funcao)
            print("length", length)
            print('comando de leitura =', command)
            print('data', data)
            return data
        else:
            logger.error(">>> ERRO: incorreto >>> PTI")
        # Mensagem recebida (ID)(funcao)(2*comprimeto ou length)(data)(CRC)

# O MODBUS trabalha com data frames que é um conjunto de bytes que está estruturado
# de forma a transferir os dados. Cada quadro tem um indicador de início e fim e
# para o JKBMS o início é de 2 bytes (em hexadecimal 4E e 57) e o final é de 1 byte
# (em hexadecimal 68). Portanto, este pedaço de código está verificando se recebemos
# uma resposta válida do JKBMS. Isso, juntamente com o CRC, nos mostrará que foram
# recebidos dados válidos que podemos usar.

# return data[4:length + 4] é usado para fatiar a data, pegar somente os dados que quiser
# https://pt.stackoverflow.com/questions/110054/como-funciona-a-atribui%C3%A7%C3%A3o-de-lista-usando-intervalo/110256#110256

