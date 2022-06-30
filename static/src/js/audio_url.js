/** @odoo-module **/

import { _t } from 'web.core';

import fieldRegistry from 'web.field_registry';
import basicFields from 'web.basic_fields';

var AudioUrlWidget = basicFields.InputField.extend({
    description: _lt("Audio URL"),
    className: 'o_audio_field_url',
    events: _.extend({}, basicFields.InputField.prototype.events, {
        'click': '_onClick',
    }),
    supportedFieldTypes: ['char'],
    isQuickEditable: true,
    
    /**
     * Urls are links in readonly mode.
     * 
     * @override
     */
    init: function () {
        this._super.apply(this, arguments);
        this.tagName = this.mode === 'readonly' ? 'div' : 'input';
        this.websitePath = this.nodeOptions.website_path || false;
        this.mime = this.nodeOptions.mime || "audio/wav";
    },

    //--------------------------------------------------------------------------
    // Public
    //--------------------------------------------------------------------------

    /**
     * Returns the associated link.
     *
     * @override
     */
    getFocusableElement: function () {
        return this.mode === 'readonly' ? this.$el.find('audio') : this._super.apply(this, arguments);
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * In readonly, the widget needs to be a link with proper href and proper
     * support for the design, which is achieved by the added classes.
     *
     * @override
     * @private
     */
    _renderReadonly: function () {
        if (!this.value) {
            return;
        }
        let href = this.value;
        if (this.value && !this.websitePath) {
            const regex = /^((ftp|http)s?:\/)?\//i; // http(s)://... ftp(s)://... /...
            href = !regex.test(this.value) ? `http://${href}` : href;
        }
        this.el.classList.add("o_form_uri", "o_text_overflow");
        const audioEl = Object.assign(document.createElement('audio', {
            controls: "controls"
        }));

        const sourceEl = Object.assign(document.createElement("source", {
            "source": href,
            "type": this.mime
        }));
        audioEl.appendChild(sourceEl);
        this.el.textContent = '';
        this.el.appendChild(audioEl);
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * Prevent the URL click from opening the record (when used on a list).
     *
     * @private
     * @param {MouseEvent} ev
     */
    _onClick: function (ev) {
        ev.stopPropagation();
    },
});

fieldRegistry.add('audio', AudioUrlWidget);
