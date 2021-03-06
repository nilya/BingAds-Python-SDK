from bingads.bulk.entities import *
from bingads.service_client import _CAMPAIGN_OBJECT_FACTORY
from bingads.internal.bulk.entities.single_record_bulk_entity import _SingleRecordBulkEntity
from bingads.internal.bulk.mappings import _SimpleBulkMapping
from bingads.internal.bulk.string_table import _StringTable
from bingads.bulk.entities.common import PerformanceData
from bingads.internal.extensions import bulk_str

_BiddableAdGroupCriterion = type(_CAMPAIGN_OBJECT_FACTORY.create('BiddableAdGroupCriterion'))
_NegativeAdGroupCriterion = type(_CAMPAIGN_OBJECT_FACTORY.create('NegativeAdGroupCriterion'))


class BulkAdGroupProductPartition(_SingleRecordBulkEntity):
    """ Represents an Ad Group Criterion that can be read or written in a bulk file.

    This class exposes the :attr:`ad_group_criterion` property that can be read and written as fields of the
    Ad Group Product Partition record in a bulk file.

    For more information, see Ad Group Product Scope at http://go.microsoft.com/fwlink/?LinkId=618642.

    *See also:*

    * :class:`.BulkServiceManager`
    * :class:`.BulkOperation`
    * :class:`.BulkFileReader`
    * :class:`.BulkFileWriter`
    """

    def __init__(self,
                 ad_group_criterion=None,
                 campaign_name=None,
                 ad_group_name=None):
        super(BulkAdGroupProductPartition, self).__init__()

        self._ad_group_criterion = ad_group_criterion
        self._campaign_name = campaign_name
        self._ad_group_name = ad_group_name
        self._performance_data = None

    @classmethod
    def _read_is_excluded(cls, entity, row_value):
        if row_value is None:
            row_value = ''
        row_value = row_value.lower()
        if row_value == 'yes' or row_value == 'true':
            is_excluded = True
        elif row_value == 'no' or row_value == 'false':
            is_excluded = False
        else:
            raise ValueError('IsExcluded can only be set to TRUE|FALSE in Ad Group Product Partition row')
        if is_excluded:
            product_partition = _CAMPAIGN_OBJECT_FACTORY.create('ProductPartition')
            product_partition.Condition = _CAMPAIGN_OBJECT_FACTORY.create('ProductCondition')
            product_partition.Type = 'ProductPartition'

            negative_ad_group_criterion = _CAMPAIGN_OBJECT_FACTORY.create('NegativeAdGroupCriterion')
            negative_ad_group_criterion.Criterion = product_partition
            negative_ad_group_criterion.Type = 'NegativeAdGroupCriterion'

            entity.ad_group_criterion = negative_ad_group_criterion
        else:
            product_partition = _CAMPAIGN_OBJECT_FACTORY.create('ProductPartition')
            product_partition.Condition = _CAMPAIGN_OBJECT_FACTORY.create('ProductCondition')
            product_partition.Type = 'ProductPartition'

            fixed_bid = _CAMPAIGN_OBJECT_FACTORY.create('FixedBid')
            fixed_bid.Type = 'FixedBid'

            biddable_ad_group_criterion = _CAMPAIGN_OBJECT_FACTORY.create('BiddableAdGroupCriterion')
            biddable_ad_group_criterion.Criterion = product_partition
            biddable_ad_group_criterion.CriterionBid = fixed_bid
            biddable_ad_group_criterion.Type = 'BiddableAdGroupCriterion'

            entity.ad_group_criterion = biddable_ad_group_criterion

    @classmethod
    def _write_bid(cls, entity):
        if isinstance(entity.ad_group_criterion, _BiddableAdGroupCriterion):
            return ad_group_bid_bulk_str(entity.ad_group_criterion.CriterionBid.Bid)
        else:
            return None

    @classmethod
    def _read_bid(cls, entity, row_value):
        if isinstance(entity.ad_group_criterion, _BiddableAdGroupCriterion):
            entity.ad_group_criterion.CriterionBid.Bid = parse_ad_group_bid(row_value)
        else:
            pass

    @classmethod
    def _write_destination_url(cls, entity):
        if isinstance(entity.ad_group_criterion, _BiddableAdGroupCriterion):
            return entity.ad_group_criterion.DestinationUrl
        else:
            return None

    @classmethod
    def _read_destination_url(cls, entity, row_value):
        if isinstance(entity.ad_group_criterion, _BiddableAdGroupCriterion):
            entity.ad_group_criterion.DestinationUrl = row_value
        else:
            pass

    _MAPPINGS = [
        _SimpleBulkMapping(
            _StringTable.IsExcluded,
            field_to_csv=lambda c: 'True' if isinstance(c.ad_group_criterion, _NegativeAdGroupCriterion) else 'False',
            csv_to_field=lambda c, v: BulkAdGroupProductPartition._read_is_excluded(c, v)
        ),
        _SimpleBulkMapping(
            _StringTable.Status,
            field_to_csv=lambda c: c.ad_group_criterion.Status,
            csv_to_field=lambda c, v: setattr(c.ad_group_criterion, 'Status', v)
        ),
        _SimpleBulkMapping(
            _StringTable.Id,
            field_to_csv=lambda c: bulk_str(c.ad_group_criterion.Id),
            csv_to_field=lambda c, v: setattr(c.ad_group_criterion, 'Id', int(v) if v else None)
        ),
        _SimpleBulkMapping(
            _StringTable.ParentId,
            field_to_csv=lambda c: bulk_str(c.ad_group_criterion.AdGroupId),
            csv_to_field=lambda c, v: setattr(c.ad_group_criterion, 'AdGroupId', int(v) if v else None)
        ),
        _SimpleBulkMapping(
            _StringTable.Campaign,
            field_to_csv=lambda c: c.campaign_name,
            csv_to_field=lambda c, v: setattr(c, 'campaign_name', v)
        ),
        _SimpleBulkMapping(
            _StringTable.AdGroup,
            field_to_csv=lambda c: c.ad_group_name,
            csv_to_field=lambda c, v: setattr(c, 'ad_group_name', v)
        ),
        _SimpleBulkMapping(
            _StringTable.SubType,
            field_to_csv=lambda c: c.ad_group_criterion.Criterion.PartitionType,
            csv_to_field=lambda c, v: setattr(c.ad_group_criterion.Criterion, 'PartitionType', v)
        ),
        _SimpleBulkMapping(
            _StringTable.ParentAdGroupCriterionId,
            field_to_csv=lambda c: bulk_str(c.ad_group_criterion.Criterion.ParentCriterionId),
            csv_to_field=lambda c, v: setattr(c.ad_group_criterion.Criterion, 'ParentCriterionId',
                                              int(v) if v else None)
        ),
        _SimpleBulkMapping(
            _StringTable.ProductCondition1,
            field_to_csv=lambda c: c.ad_group_criterion.Criterion.Condition.Operand,
            csv_to_field=lambda c, v: setattr(c.ad_group_criterion.Criterion.Condition, 'Operand', v)
        ),
        _SimpleBulkMapping(
            _StringTable.ProductValue1,
            field_to_csv=lambda c: c.ad_group_criterion.Criterion.Condition.Attribute,
            csv_to_field=lambda c, v: setattr(c.ad_group_criterion.Criterion.Condition, 'Attribute', v)
        ),
        _SimpleBulkMapping(
            _StringTable.Bid,
            field_to_csv=lambda c: BulkAdGroupProductPartition._write_bid(c),
            csv_to_field=lambda c, v: BulkAdGroupProductPartition._read_bid(c, v)
        ),
        _SimpleBulkMapping(
            _StringTable.DestinationUrl,
            field_to_csv=lambda c: BulkAdGroupProductPartition._write_destination_url(c),
            csv_to_field=lambda c, v: BulkAdGroupProductPartition._read_destination_url(c, v)
        )
    ]

    @property
    def ad_group_criterion(self):
        """ Defines an Ad Group Criterion """

        return self._ad_group_criterion

    @ad_group_criterion.setter
    def ad_group_criterion(self, ad_group_criterion):
        self._ad_group_criterion = ad_group_criterion

    @property
    def campaign_name(self):
        """ Defines the name of the Campaign.

        :rtype: str
        """

        return self._campaign_name

    @campaign_name.setter
    def campaign_name(self, campaign_name):
        self._campaign_name = campaign_name

    @property
    def ad_group_name(self):
        """ Defines the name of the Ad Group

        :rtype: str
        """

        return self._ad_group_name

    @ad_group_name.setter
    def ad_group_name(self, ad_group_name):
        self._ad_group_name = ad_group_name

    @property
    def performance_data(self):
        return self._performance_data

    def process_mappings_to_row_values(self, row_values, exclude_readonly_data):
        self._validate_property_not_null(self.ad_group_criterion, 'ad_group_criterion')
        self.convert_to_values(row_values, BulkAdGroupProductPartition._MAPPINGS)

        if not exclude_readonly_data:
            PerformanceData.write_to_row_values_if_not_null(self._performance_data, row_values)

    def process_mappings_from_row_values(self, row_values):
        row_values.convert_to_entity(self, BulkAdGroupProductPartition._MAPPINGS)

        self._performance_data = PerformanceData.read_from_row_values_or_null(row_values)

    def read_additional_data(self, stream_reader):
        super(BulkAdGroupProductPartition, self).read_additional_data(stream_reader)
