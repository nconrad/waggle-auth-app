from django.db import models


class NodeData(models.Model):
    vsn = models.CharField("VSN", max_length=30, unique="True")
    name = models.CharField(max_length=30)
    tags = models.ManyToManyField("Tag", blank=True)
    computes = models.ManyToManyField("ComputeHardware", through="Compute", related_name="computes")
    resources = models.ManyToManyField("ResourceHardware", through="Resource", related_name="resources")
    gps_lat = models.FloatField("Latitude", blank=True, null=True)
    gps_lon = models.FloatField("Longitude", blank=True, null=True)

    def __str__(self):
         return self.vsn

    class Meta:
        verbose_name_plural = "Nodes"


class AbstractHardware(models.Model):
    hardware = models.CharField(max_length=100)
    hw_model = models.CharField(max_length=30, blank=True)
    hw_version = models.CharField(max_length=30, blank=True)
    sw_version = models.CharField(max_length=30, blank=True)
    manufacturer = models.CharField(max_length=255, default="", blank=True)
    datasheet = models.CharField(max_length=255, default="", blank=True)
    capabilities = models.ManyToManyField("Capability", blank=True)
    description = models.TextField(blank=True)

    class Meta:
        abstract = True


class ComputeHardware(AbstractHardware):
    cpu = models.CharField(max_length=30, blank=True)
    cpu_ram = models.CharField(max_length=30, blank=True)
    gpu_ram = models.CharField(max_length=30, blank=True)
    shared_ram = models.BooleanField(default=False, blank=True)

    def __str__(self):
        return self.hardware

    class Meta:
        verbose_name_plural = "Compute Hardware"


class ResourceHardware(AbstractHardware):

    def __str__(self):
        return self.hardware

    class Meta:
        verbose_name_plural = "Resource Hardware"


class SensorHardware(AbstractHardware):

    def __str__(self):
        return self.hardware

    class Meta:
        verbose_name_plural = "Sensor Hardware"


class Capability(models.Model):
    capability = models.CharField(max_length=30)

    def __str__(self):
         return self.capability

    class Meta:
        verbose_name_plural = "Capabilities"


class Compute(models.Model):

    ZONE_CHOICES = (
        ("core", "core"),
        ("agent", "agent"),
        ("shield", "shield"),
        ("detector", "detector (deprecated! use enclosure instead!)"),
        ("enclosure", "enclosure"),
    )

    node = models.ForeignKey(NodeData, on_delete=models.CASCADE, blank=True)
    hardware = models.ForeignKey(ComputeHardware, on_delete=models.CASCADE, blank=True)
    name = models.CharField(max_length=30, default="", blank=True)
    serial_no = models.CharField(max_length=30, default="", blank=True)
    zone = models.CharField(max_length=30, choices=ZONE_CHOICES, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Compute"


class AbstractSensor(models.Model):
    hardware = models.ForeignKey(SensorHardware, on_delete=models.CASCADE, blank=True)
    name = models.CharField(max_length=30, blank=True)
    labels = models.ManyToManyField("Label", blank=True)
    serial_no = models.CharField(max_length=30, default="", blank=True)
    uri = models.CharField(max_length=256, default="", blank=True)

    class Meta:
        abstract = True


class NodeSensor(AbstractSensor):
    node = models.ForeignKey(NodeData, on_delete=models.CASCADE, blank=True)
    scope = models.CharField(max_length=30, default="global", blank=True)


class ComputeSensor(AbstractSensor):
    scope = models.ForeignKey(Compute, on_delete=models.CASCADE, blank=True)


class Resource(models.Model):
    node = models.ForeignKey(NodeData, on_delete=models.CASCADE, blank=True)
    hardware = models.ForeignKey(ResourceHardware, on_delete=models.CASCADE, blank=True)
    name = models.CharField(max_length=30, blank=True)

    def __str__(self):
        return self.name


class Tag(models.Model):
    tag = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.tag

    def natural_key(self):
        return self.tag


class Label(models.Model):
    label = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.label

    def natural_key(self):
        return self.label
