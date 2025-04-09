from PySide6.QtCore import QObject, Signal, Property

class DeviceEntitie(QObject):
    temperatureChanged = Signal(int)
    humidityChanged = Signal(int)
    weightChanged = Signal(int)
    temperatureActualChanged = Signal(int)
    humidityActualChanged = Signal(int)
    airPurityChanged = Signal(int)
    timeActualChanged = Signal(int, int)
    timeTargetChanged = Signal(int, int)
    pauseChanged = Signal(bool)
    automatizationChanged = Signal(bool)

    def __init__(self, data):
        super().__init__()

        self.id = data["id"]    

        self._automatization = data["automatization"]
        self._temperature = data["temperature"]
        self.pre_set = data["pre_set"]
        self._humidity = data["humidity"]
        self._weight = data["weight"]
        self._humidity_actual = data["humidity_actual"]
        self._temperature_actual = data["temperature_actual"]
        self._hours_actual = data["hours_actual"]
        self._minute_actual = data["minute_actual"]
        self._airPurity = data["airPurity"]
        self._hours = data["hours"]
        self._minutes = data["minutes"]
        self.histories = data["histories"]# Puede llenarse con objetos History, opcional
        self._pause = data["pause"]

    # ------- PROPIEDADES CON SEÑALES -------

    def get_temperature(self): return self._temperature
    def set_temperature(self, value):
        if self._temperature != value:
            self._temperature = value
            self.temperatureChanged.emit(value)
    temperature = Property(int, get_temperature, set_temperature, notify=temperatureChanged)

    def get_humidity(self): return self._humidity
    def set_humidity(self, value):
        if self._humidity != value:
            self._humidity = value
            self.humidityChanged.emit(value)
    humidity = Property(int, get_humidity, set_humidity, notify=humidityChanged)

    def get_weight(self): return self._weight
    def set_weight(self, value):
        if self._weight != value:
            self._weight = value
            self.weightChanged.emit(value)
    weight = Property(int, get_weight, set_weight, notify=weightChanged)

    def get_temperature_actual(self): return self._temperature_actual
    def set_temperature_actual(self, value):
        if self._temperature_actual != value:
            self._temperature_actual = value
            self.temperatureActualChanged.emit(value)
    temperature_actual = Property(int, get_temperature_actual, set_temperature_actual, notify=temperatureActualChanged)

    def get_humidity_actual(self): return self._humidity_actual
    def set_humidity_actual(self, value):
        if self._humidity_actual != value:
            self._humidity_actual = value
            self.humidityActualChanged.emit(value)
    humidity_actual = Property(int, get_humidity_actual, set_humidity_actual, notify=humidityActualChanged)

    def get_air_purity(self): return self._airPurity
    def set_air_purity(self, value):
        if self._airPurity != value:
            self._airPurity = value
            self.airPurityChanged.emit(value)
    airPurity = Property(int, get_air_purity, set_air_purity, notify=airPurityChanged)

    def get_hours_actual(self): return self._hours_actual
    def set_hours_actual(self, value):
        if self._hours_actual != value:
            self._hours_actual = value
            self.timeActualChanged.emit(self._hours_actual, self._minute_actual)

    def get_minute_actual(self): return self._minute_actual
    def set_minute_actual(self, value):
        if self._minute_actual != value:
            self._minute_actual = value
            self.timeActualChanged.emit(self._hours_actual, self._minute_actual)

    def get_hours(self): return self._hours
    def set_hours(self, value):
        if self._hours != value:
            self._hours = value
            self.timeTargetChanged.emit(self._hours, self._minutes)

    def get_minutes(self): return self._minutes
    def set_minutes(self, value):
        if self._minutes != value:
            self._minutes = value
            self.timeTargetChanged.emit(self._hours, self._minutes)

    def get_pause(self): return self._pause
    def set_pause(self, value):
        self._pause = value
        self.pauseChanged.emit(value)
    pause = Property(bool, get_pause, set_pause, notify=pauseChanged)

    def get_automatization(self): return self._automatization
    def set_automatization(self, value):
        if self._automatization != value:
            self._automatization = value
            self.automatizationChanged.emit(value)
    automatization = Property(bool, get_automatization, set_automatization, notify=automatizationChanged)
