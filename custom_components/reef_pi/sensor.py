"""Platform for reef-pi sensor integration."""
from homeassistant.const import CONF_NAME, TEMP_CELSIUS, TEMP_FAHRENHEIT, DEGREE
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import _LOGGER, DOMAIN


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Add an temperature entity from a config_entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    base_name = coordinator.info["name"] + "_"
    sensors = [
        ReefPiTemperature(id, base_name + tcs["name"], coordinator)
        for id, tcs in coordinator.tcs.items()
    ]
    ph_sensors = [
        ReefPiPh(id, base_name + ph["name"], coordinator)
        for id, ph in coordinator.ph.items()
    ]
    _LOGGER.debug("sensor base name: %s, temperature: %d, pH: %d", base_name, len(sensors), len(ph_sensors))
    async_add_entities(sensors)
    async_add_entities(ph_sensors)
    async_add_entities([ReefPiBaicInfo(coordinator)])


class ReefPiBaicInfo(CoordinatorEntity):
    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.api = coordinator

    @property
    def icon(self):
        return "mdi:fishbowl-outline"

    @property
    def name(self):
        """Return the name of the sensor"""
        if not self.api.info or not "name" in self.api.info:
            return "ReefPiBaicInfo"
        return self.api.info["name"]

    @property
    def unique_id(self):
        """Return a unique_id for this entity."""
        return f"{self.coordinator.unique_id}_info"

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return TEMP_CELSIUS

    @property
    def available(self):
        """Return if teperature"""
        return self.api.info and "name" in self.api.info

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.api.info["cpu_temperature"]

    @property
    def device_state_attributes(self):
        if self.api.info:
            return self.api.info
        return {}


class ReefPiTemperature(CoordinatorEntity):
    def __init__(self, id, name, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._id = id
        self._name = name
        self.api = coordinator

    @property
    def name(self):
        """Return the name of the sensor"""
        return self._name

    @property
    def unique_id(self):
        """Return a unique_id for this entity."""
        return f"{self.coordinator.unique_id}_tcs_{self._id}"

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        if self.available and self.api.tcs[self._id]["fahrenheit"]:
            return TEMP_FAHRENHEIT
        return TEMP_CELSIUS

    @property
    def available(self):
        """Return if teperature"""
        return self._id in self.api.tcs.keys()

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.api.tcs[self._id]["temperature"]

    @property
    def device_state_attributes(self):
        return self.api.tcs[self._id]["attributes"]

class ReefPiPh(CoordinatorEntity):
    def __init__(self, id, name, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._id = id
        self._name = name
        self.api = coordinator

    @property
    def name(self):
        """Return the name of the sensor"""
        return self._name

    @property
    def unique_id(self):
        """Return a unique_id for this entity."""
        return f"{self.coordinator.unique_id}_ph_{self._id}"

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return DEGREE

    @property
    def available(self):
        """Return if teperature"""
        return self._id in self.api.ph.keys()

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.api.ph[self._id]["value"]

    @property
    def device_state_attributes(self):
        return self.api.ph[self._id]["attributes"]