// --- Bilingual English <-> Bangla (বাংলা) Language Engine ---
function getAppLanguage() {
    return localStorage.getItem('app_lang') || 'en';
}

function setAppLanguage(lang) {
    localStorage.setItem('app_lang', lang);
    document.cookie = `app_lang=${lang}; path=/; max-age=31536000`;
    applyLanguage(lang);
}

function toggleLanguage() {
    const currentLang = getAppLanguage();
    const newLang = currentLang === 'en' ? 'bn' : 'en';
    setAppLanguage(newLang);
}

function applyLanguage(lang) {
    if (typeof TRANSLATIONS === 'undefined' || !TRANSLATIONS[lang]) return;
    const dict = TRANSLATIONS[lang];

    // Translate all elements with data-i18n
    const elements = document.querySelectorAll('[data-i18n]');
    elements.forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (dict[key]) {
            el.textContent = dict[key];
        }
    });

    // Translate placeholder attributes with data-i18n-ph
    const phElements = document.querySelectorAll('[data-i18n-ph]');
    phElements.forEach(el => {
        const key = el.getAttribute('data-i18n-ph');
        if (dict[key]) {
            el.placeholder = dict[key];
        }
    });

    // Update toggle button text
    const btnLabels = document.querySelectorAll('.lang-btn-text');
    btnLabels.forEach(lbl => {
        lbl.textContent = lang === 'en' ? 'বাংলা' : 'English';
    });

    const activeBadges = document.querySelectorAll('.lang-active-badge');
    activeBadges.forEach(badge => {
        badge.textContent = lang === 'en' ? 'EN' : 'BN';
    });

    // Update html lang attribute
    document.documentElement.lang = lang;
}

document.addEventListener('DOMContentLoaded', () => {
    // Flash Alert Dismissal
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            alert.style.transition = 'opacity 0.5s ease';
            setTimeout(() => alert.remove(), 500);
        }, 5000);
    });

    // Apply Language
    applyLanguage(getAppLanguage());
});

// Modal Helper Functions
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('active');
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('active');
    }
}

// Table Search Filter
function filterTable(inputId, tableId) {
    const input = document.getElementById(inputId);
    const filter = input.value.toLowerCase();
    const table = document.getElementById(tableId);
    const rows = table.getElementsByTagName('tr');

    for (let i = 1; i < rows.length; i++) {
        let cells = rows[i].getElementsByTagName('td');
        let match = false;
        for (let j = 0; j < cells.length; j++) {
            if (cells[j] && cells[j].textContent.toLowerCase().indexOf(filter) > -1) {
                match = true;
                break;
            }
        }
        rows[i].style.display = match ? '' : 'none';
    }
}

// Repair Receipt Modal Printer with Dynamic Shop Settings (Bangladeshi Taka)
function printRepairReceipt(id, customer, phone, device, problem, cost, advance, status, delivery, date) {
    const balance = (parseFloat(cost) - parseFloat(advance)).toFixed(2);
    const shop = window.SHOP_SETTINGS || {
        name: 'SS Technology',
        tagline: 'Electronics Shop & Repair Center',
        phone: '01700000000',
        address: 'Club Super Market 2nd FloorChapainawabganj'
    };

    const receiptHTML = `
        <div id="printableReceipt" style="font-family: Arial, sans-serif; color: #111; padding: 20px; border: 2px solid #333; max-width: 520px; margin: auto; background: #fff;">
            <div style="text-align: center; border-bottom: 2px solid #333; padding-bottom: 10px; margin-bottom: 15px;">
                <h2 style="margin: 0; text-transform: uppercase; letter-spacing: 1px;">${shop.name}</h2>
                <p style="margin: 4px 0; font-size: 0.9rem; color: #444;">${shop.tagline}</p>
                <p style="margin: 0; font-size: 0.8rem; color: #666;">Phone: ${shop.phone} | ${shop.address}</p>
                <h4 style="margin-top: 10px; margin-bottom: 0; background: #222; color: #fff; padding: 4px; font-size: 0.9rem;">REPAIR SERVICE RECEIPT</h4>
            </div>
            
            <div style="display: flex; justify-content: space-between; margin-bottom: 12px; font-size: 0.9rem; font-weight: bold;">
                <span>Servicing Memo #: ${id}</span>
                <span>Date: ${date}</span>
            </div>
            
            <hr style="border: 0.5px solid #ccc; margin-bottom: 12px;">
            
            <p style="margin: 4px 0;"><strong>Customer Name:</strong> ${customer}</p>
            <p style="margin: 4px 0;"><strong>Contact Phone:</strong> ${phone || 'N/A'}</p>
            <p style="margin: 4px 0;"><strong>Device Item:</strong> ${device}</p>
            <p style="margin: 4px 0;"><strong>Reported Issue:</strong> ${problem}</p>
            <p style="margin: 4px 0;"><strong>Est. Delivery Date:</strong> ${delivery || 'TBD'}</p>
            <p style="margin: 4px 0;"><strong>Status:</strong> <span style="text-transform: uppercase; font-weight: bold;">${status}</span></p>
            
            <table style="width: 100%; border-collapse: collapse; margin-top: 15px;">
                <tr style="background: #f0f0f0;">
                    <th style="padding: 8px; border: 1px solid #ddd; text-align: left;">Item / Description</th>
                    <th style="padding: 8px; border: 1px solid #ddd; text-align: right;">Amount (Tk)</th>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;">Repair Labor & Replacement Parts Charge</td>
                    <td style="padding: 8px; border: 1px solid #ddd; text-align: right;">Tk ${parseFloat(cost).toFixed(2)}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold;">Advance Paid</td>
                    <td style="padding: 8px; border: 1px solid #ddd; text-align: right; color: green; font-weight: bold;">-Tk ${parseFloat(advance).toFixed(2)}</td>
                </tr>
                <tr style="background: #f9f9f9;">
                    <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold; font-size: 1rem;">Balance Due</td>
                    <td style="padding: 8px; border: 1px solid #ddd; text-align: right; font-weight: bold; font-size: 1rem; color: red;">Tk ${balance}</td>
                </tr>
            </table>

            <div style="margin-top: 30px; display: flex; justify-content: space-between; align-items: flex-end; font-size: 0.85rem;">
                <div style="text-align: center;">
                    <br><br>
                    ______________________<br>
                    Customer Signature
                </div>
                <div style="text-align: center;">
                    <div style="font-family: 'Brush Script MT', cursive, sans-serif; font-size: 1.35rem; color: #1e3a8a; font-weight: bold; font-style: italic; border-bottom: 2px dashed #1e3a8a; padding: 0 10px; display: inline-block;">
                        ${shop.name} Auth
                    </div>
                    <div style="font-size: 0.8rem; font-weight: bold; color: #333; margin-top: 3px;">Authorized Technician</div>
                </div>
            </div>
            
            <p style="text-align: center; font-size: 0.75rem; color: #777; margin-top: 25px;">Thank you for choosing ${shop.name}! Please bring this receipt for pickup.</p>
        </div>
    `;

    let receiptContainer = document.getElementById('receiptModalBody');
    if (receiptContainer) {
        receiptContainer.innerHTML = receiptHTML;
        openModal('receiptModal');
    }
}

// Product Sales Cash Memo Invoice Printer (Bangladeshi Taka & EMI Support)
function printSalesReceipt(saleId, date, pcode, pname, cname, ccode, qty, unitPrice, revenue, soldBy, paidAmount, dueAmount, paymentType, paymentStatus, emiMonths, monthlyInstallment, nextDueDate) {
    const shop = window.SHOP_SETTINGS || {
        name: 'SS Technology',
        tagline: 'Electronics Shop & Repair Center',
        phone: '01700000000',
        address: 'Club Super Market 2nd Floor,Chapainawabganj'
    };

    const formattedSaleId = String(saleId).startsWith('SLS-') ? saleId : `SLS-${saleId}`;
    const paid = parseFloat(paidAmount !== undefined && paidAmount !== null && paidAmount !== '' ? paidAmount : revenue);
    const due = parseFloat(dueAmount !== undefined && dueAmount !== null && dueAmount !== '' ? dueAmount : 0);

    const receiptHTML = `
        <div id="printableReceipt" style="font-family: Arial, sans-serif; color: #111; padding: 20px; border: 2px solid #333; max-width: 520px; margin: auto; background: #fff;">
            <div style="text-align: center; border-bottom: 2px solid #333; padding-bottom: 10px; margin-bottom: 15px;">
                <h2 style="margin: 0; text-transform: uppercase; letter-spacing: 1px;">${shop.name}</h2>
                <p style="margin: 4px 0; font-size: 0.9rem; color: #444;">${shop.tagline}</p>
                <p style="margin: 0; font-size: 0.8rem; color: #666;">Phone: ${shop.phone} | ${shop.address}</p>
                <h4 style="margin-top: 10px; margin-bottom: 0; background: #10b981; color: #fff; padding: 4px; font-size: 0.9rem;">OFFICIAL SALES CASH MEMO</h4>
            </div>
            
            <div style="display: flex; justify-content: space-between; margin-bottom: 12px; font-size: 0.9rem;">
                <span><strong>Sales Memo #:</strong> ${formattedSaleId}</span>
                <span><strong>Date:</strong> ${date}</span>
            </div>
            
            <div style="display: flex; justify-content: space-between; margin-bottom: 12px; font-size: 0.9rem;">
                <span><strong>Customer:</strong> ${cname} (${ccode})</span>
                <span><strong>Billed By:</strong> ${soldBy}</span>
            </div>
            
            <hr style="border: 0.5px solid #ccc; margin-bottom: 12px;">
            
            <table style="width: 100%; border-collapse: collapse; margin-top: 10px;">
                <thead>
                    <tr style="background: #f0f0f0;">
                        <th style="padding: 8px; border: 1px solid #ddd; text-align: left;">Product Item</th>
                        <th style="padding: 8px; border: 1px solid #ddd; text-align: center;">Qty</th>
                        <th style="padding: 8px; border: 1px solid #ddd; text-align: right;">Unit Price</th>
                        <th style="padding: 8px; border: 1px solid #ddd; text-align: right;">Total (Tk)</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd;">${pname} <br><small style="color:#666;">Code: ${pcode}</small></td>
                        <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">${qty}</td>
                        <td style="padding: 8px; border: 1px solid #ddd; text-align: right;">Tk ${parseFloat(unitPrice).toFixed(2)}</td>
                        <td style="padding: 8px; border: 1px solid #ddd; text-align: right; font-weight: bold;">Tk ${parseFloat(revenue).toFixed(2)}</td>
                    </tr>
                    <tr style="background: #f9f9f9;">
                        <td colspan="3" style="padding: 8px; border: 1px solid #ddd; text-align: right; font-weight: bold; font-size: 0.95rem;">Total Bill Amount:</td>
                        <td style="padding: 8px; border: 1px solid #ddd; text-align: right; font-weight: bold; font-size: 1rem;">Tk ${parseFloat(revenue).toFixed(2)}</td>
                    </tr>
                    <tr>
                        <td colspan="3" style="padding: 8px; border: 1px solid #ddd; text-align: right; font-weight: bold; color: green; font-size: 0.95rem;">Paid Amount Today:</td>
                        <td style="padding: 8px; border: 1px solid #ddd; text-align: right; font-weight: bold; color: green; font-size: 1rem;">Tk ${paid.toFixed(2)}</td>
                    </tr>
                    ${due > 0 ? `
                    <tr style="background: #fff0f0;">
                        <td colspan="3" style="padding: 8px; border: 1px solid #ddd; text-align: right; font-weight: bold; color: red; font-size: 0.95rem;">Remaining Due Balance:</td>
                        <td style="padding: 8px; border: 1px solid #ddd; text-align: right; font-weight: bold; color: red; font-size: 1rem;">Tk ${due.toFixed(2)}</td>
                    </tr>
                    ` : ''}
                </tbody>
            </table>

            ${paymentType === 'EMI / Installment' ? `
            <div style="margin-top: 15px; padding: 10px; background: rgba(168, 85, 247, 0.08); border: 1px dashed #a855f7; border-radius: 6px; font-size: 0.82rem; color: #4c1d95;">
                <strong style="font-size: 0.88rem; text-transform: uppercase;"> EMI / Installment Plan Details:</strong><br>
                <span>Plan Tenure: <strong>${emiMonths || 6} Months</strong> | Monthly Installment: <strong style="color: #7e22ce;">Tk ${parseFloat(monthlyInstallment || 0).toFixed(2)}</strong></span><br>
                <span>Next Installment Due Date: <strong>${nextDueDate || 'TBD'}</strong></span>
            </div>
            ` : ''}

            <div style="margin-top: 30px; display: flex; justify-content: space-between; align-items: flex-end; font-size: 0.85rem;">
                <div style="text-align: center;">
                    <br><br>
                    ______________________<br>
                    Customer Signature
                </div>
                <div style="text-align: center;">
                    <div style="font-family: 'Brush Script MT', cursive, sans-serif; font-size: 1.35rem; color: #10b981; font-weight: bold; font-style: italic; border-bottom: 2px dashed #10b981; padding: 0 10px; display: inline-block;">
                        ${shop.name} Sales
                    </div>
                    <div style="font-size: 0.8rem; font-weight: bold; color: #333; margin-top: 3px;">Authorized Seller</div>
                </div>
            </div>
            
            <p style="text-align: center; font-size: 0.75rem; color: #777; margin-top: 25px;">Thank you for shopping at ${shop.name}! Please keep this receipt for warranty claims.</p>
        </div>
    `;

    let salesReceiptContainer = document.getElementById('salesReceiptModalBody');
    if (salesReceiptContainer) {
        salesReceiptContainer.innerHTML = receiptHTML;
        openModal('salesReceiptModal');
    }
}
