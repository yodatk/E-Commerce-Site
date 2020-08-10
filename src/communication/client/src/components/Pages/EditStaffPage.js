import React, {Component} from "react";
import {MDBBtn, MDBCol, MDBContainer, MDBInput, MDBRow} from 'mdbreact';
import PropTypes from "prop-types";
import FormUtils from "../FormUtils";
import axios from "axios";
import * as HttpStatus from "http-status-codes"
import {Redirect, withRouter} from "react-router-dom";


class EditStaffPage extends Component {
    state = {

        store_name: this.props.match.params.store_name,
        user: this.props.match.params.user,
        appointed_by: this.props.match.params.appointed_by,
        can_manage_inventory: this.props.match.params.can_manage_inventory === "true",
        can_manage_discount: this.props.match.params.can_manage_discount === "true",
        open_and_close_store: this.props.match.params.open_and_close_store === "true",
        watch_purchase_history: this.props.match.params.watch_purchase_history === "true",
        appoint_new_store_manager: this.props.match.params.appoint_new_store_manager === "true",
        appoint_new_store_owner: this.props.match.params.appoint_new_store_owner === "true",
        msg: "",
        redirectAfterEdit: null
    };
    formUtils = new FormUtils();

    onChange = (e) => {
        this.setState({[e.target.name]: e.target.checked});
    }


    sendIfPossible = () => {
        axios.post(
            "/edit_permissions",
            {
                user_id: this.props.getUserId(),
                edited_user: this.state.user,
                store_name: this.state.store_name,
                can_manage_inventory: this.state.can_manage_inventory,
                can_manage_discount: this.state.can_manage_discount,
                open_and_close_store: this.state.open_and_close_store,
                watch_purchase_history: this.state.watch_purchase_history,
                appoint_new_store_manager: this.state.appoint_new_store_manager,
                appoint_new_store_owner: this.state.appoint_new_store_owner,
            },
        )
            .then((res) => {
                this.dealWithEditResult(res);
            }).catch(error => {
            console.log(error)
            this.dealWithEditResult(error.response);
        });
    }

    dealWithEditResult = (res) => {
        if(res){
            if (res.status === HttpStatus.CREATED || res.status === HttpStatus.OK) {
                // register successful
                this.setState({redirectAfterEdit: `/store_page/${this.state.store_name}`})
            } else {
                this.setState({msg: this.convertErrorToMessage(res.data["error"])})
            }
        }

    }

    convertErrorToMessage = (msg) => {
        if (msg) {
            msg = msg.split("|").join(", ");
            msg = msg.split("_").join(" ");
            return msg;
        }
    }


    onSubmit = (e) => {
        e.preventDefault();
        this.sendIfPossible();

    }

    render() {
        if (this.state.redirectAfterEdit) {
            return <Redirect to={this.state.redirectAfterEdit}/>
        } else {
            return (
                <React.Fragment>
                    <MDBContainer style={{padding: "10px"}}>
                        <MDBRow
                            style={{
                                display: "flex",
                                alignItems: "center",
                                justifyContent: "center",
                            }}>
                            <MDBCol md="6">
                                <form className="needs-validation" onSubmit={this.onSubmit} noValidate>
                                    <p onChange={this.onChange}
                                       className="h3 text-center mb-4">{`Edit Permissions for ${this.state.user}`}</p>
                                    <div className="grey-text">
                                        <div className="form-group">
                                            <div className='custom-control custom-switch'>
                                                <input
                                                    type='checkbox'
                                                    className='custom-control-input'
                                                    id='can_manage_inventory'
                                                    name='can_manage_inventory'
                                                    value={this.state.can_manage_inventory}
                                                    checked={this.state.can_manage_inventory}
                                                    onChange={this.onChange}
                                                    readOnly
                                                />
                                                <label className='custom-control-label' htmlFor='can_manage_inventory'>
                                                    Inventory Management
                                                </label>
                                            </div>
                                            <div className='custom-control custom-switch'>
                                                <input
                                                    type='checkbox'
                                                    className='custom-control-input'
                                                    id='can_manage_discount'
                                                    name='can_manage_discount'
                                                    value={this.state.can_manage_discount}
                                                    checked={this.state.can_manage_discount}
                                                    onChange={this.onChange}
                                                    readOnly
                                                />
                                                <label className='custom-control-label' htmlFor='can_manage_discount'>
                                                    Discount Management
                                                </label>
                                            </div>
                                            <div className='custom-control custom-switch'>
                                                <input
                                                    type='checkbox'
                                                    className='custom-control-input'
                                                    id='open_and_close_store'
                                                    name='open_and_close_store'
                                                    value={this.state.open_and_close_store}
                                                    checked={this.state.open_and_close_store}
                                                    onChange={this.onChange}
                                                    readOnly
                                                />
                                                <label className='custom-control-label' htmlFor='open_and_close_store'>
                                                    Open or Close Store
                                                </label>
                                            </div>
                                            <div className='custom-control custom-switch'>
                                                <input
                                                    type='checkbox'
                                                    className='custom-control-input'
                                                    id='watch_purchase_history'
                                                    name='watch_purchase_history'
                                                    value={this.state.watch_purchase_history}
                                                    checked={this.state.watch_purchase_history}
                                                    onChange={this.onChange}
                                                    readOnly
                                                />
                                                <label className='custom-control-label'
                                                       htmlFor='watch_purchase_history'>
                                                    Watch Purchase History
                                                </label>
                                            </div>
                                            <div className='custom-control custom-switch'>
                                                <input
                                                    type='checkbox'
                                                    className='custom-control-input'
                                                    id='appoint_new_store_manager'
                                                    name='appoint_new_store_manager'
                                                    value={this.state.appoint_new_store_manager}
                                                    checked={this.state.appoint_new_store_manager}
                                                    onChange={this.onChange}
                                                    readOnly
                                                />
                                                <label className='custom-control-label'
                                                       htmlFor='appoint_new_store_manager'>
                                                    Appoint New Manager
                                                </label>
                                            </div>
                                            {/*<div className='custom-control custom-switch'>*/}
                                            {/*    <input*/}
                                            {/*        type='checkbox'*/}
                                            {/*        className='custom-control-input'*/}
                                            {/*        id='appoint_new_store_owner'*/}
                                            {/*        name='appoint_new_store_owner'*/}
                                            {/*        value={this.state.appoint_new_store_owner}*/}
                                            {/*        checked={this.state.appoint_new_store_owner}*/}
                                            {/*        onChange={this.onChange}*/}
                                            {/*        readOnly*/}
                                            {/*    />*/}
                                            {/*    <label className='custom-control-label'*/}
                                            {/*           htmlFor='appoint_new_store_owner'>*/}
                                            {/*        Appoint new Owner*/}
                                            {/*    </label>*/}
                                            {/*</div>*/}
                                        </div>
                                    </div>
                                    <div className="text-center">
                                        <MDBBtn type="submit"
                                                value="Submit"
                                                outline
                                                color="info">Submit</MDBBtn>
                                    </div>
                                </form>
                                <p onChange={this.onChange}
                                   className="h3 text-center mb-4 text-danger">{this.state.msg}</p>
                            </MDBCol>
                        </MDBRow>
                    </MDBContainer>
                </React.Fragment>
            );
        }
    }
}


// PropTypes
EditStaffPage.propTypes = {
    isLoggedIn: PropTypes.func.isRequired,
    isAdmin: PropTypes.func.isRequired,
    updateParent: PropTypes.func.isRequired,
    getUserName: PropTypes.func.isRequired,

};

export default withRouter(EditStaffPage);

